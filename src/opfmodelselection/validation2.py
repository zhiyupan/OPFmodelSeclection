"""Validation2.0 batch recommendation utilities.

This module runs the current KG-backed online recommendation pipeline over a
fixed set of fifty-four requirement cases and saves the resulting Top-3 rankings.
The notebook and GUI both import this module so the validation logic stays in
one place.
"""

from __future__ import annotations

import json
import contextlib
import io
import math
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from .config import (
    MODEL_NAME,
    make_project_paths_portable,
    ONLINE_RECOMMENDATION_INTERMEDIATE_DIR,
    ONLINE_RECOMMENDATION_OUTPUT_DIR,
    RECOMMENDATION_VALIDATION_RESULTS_DIR,
    RECOMMENDATION_HUMAN_GOLD_CSV,
)
from .online_recommendation import run_direct_online_recommendation_pipeline
from .prompt_loader import prompt_fingerprint
from .user_requirements import USER_REQUIREMENTS


ONLINE_RECOMMENDATION_PROMPT_IDS = (
    "common.soft_schema_instruction",
    "online_recommendation.prefilter.system",
    "online_recommendation.prefilter.user",
    "online_recommendation.prefilter.retry_invalid_json",
    "online_recommendation.prefilter_schema_descriptions.instance_name",
    "online_recommendation.prefilter_schema_descriptions.prefilter_score",
    "online_recommendation.prefilter_schema_descriptions.why_matched",
    "online_recommendation.prefilter_schema_descriptions.main_risk_or_gap",
    "online_recommendation.prefilter_schema_descriptions.supporting_evidence",
    "online_recommendation.close_reading.system",
    "online_recommendation.close_reading.user",
)


def current_online_recommendation_prompt_hash() -> str:
    """Hash the prompt text currently on disk for resume/cache validation."""
    return prompt_fingerprint(*ONLINE_RECOMMENDATION_PROMPT_IDS)


VALIDATION2_RECOMMENDATION_INTERMEDIATE_DIR = ONLINE_RECOMMENDATION_INTERMEDIATE_DIR
VALIDATION2_RECOMMENDATION_OUTPUT_DIR = ONLINE_RECOMMENDATION_OUTPUT_DIR
VALIDATION2_METRICS_OUTPUT_DIR = RECOMMENDATION_VALIDATION_RESULTS_DIR
VALIDATION2_TOP3_CSV = (
    VALIDATION2_RECOMMENDATION_OUTPUT_DIR
    / "01_validation_batch_top3_recommendations.csv"
)
VALIDATION2_RAW_JSON = (
    VALIDATION2_RECOMMENDATION_INTERMEDIATE_DIR
    / "01_validation_batch_full_run_records.json"
)
VALIDATION2_ACCURACY_BY_REQUIREMENT_CSV = (
    VALIDATION2_METRICS_OUTPUT_DIR / "01_scores_by_requirement.csv"
)
VALIDATION2_ACCURACY_SUMMARY_CSV = (
    VALIDATION2_METRICS_OUTPUT_DIR / "02_overall_scores.csv"
)

VALIDATION2_TABLE_COLUMNS = [
    "Requirement ID",
    "Requirement group",
    "Requirement name",
    "Requirement text",
    "Top rank",
    "Instance",
    "Model name",
    "PDF file",
    "Paper title",
    "Final score",
    "Recommendation reason",
    "Matched needs",
    "Strengths",
    "Limitations",
    "Simple explanation",
    "Objective text",
    "Constraint text",
    "Parameter text",
    "Mathematical problem types",
    "Technologies",
    "Sectors",
]


GOLD_ACCEPTABLE_MODEL_COLUMNS = [f"acceptable_model_{index}" for index in range(1, 8)]
GOLD_RANK_MODEL_COLUMNS = [f"rank_{index}_model" for index in range(1, 4)]
GOLD_RANK_RELEVANCE_COLUMNS = [f"rank_{index}_relevance" for index in range(1, 4)]
RECOMMENDATION_HUMAN_GOLD_COLUMNS = [
    "requirement_id",
    "requirement_group",
    "requirement_name",
    "requirement_text",
    "gold_standard_type",
    "evaluation_metric",
    "gold_model_count",
    *GOLD_ACCEPTABLE_MODEL_COLUMNS,
    "rank_1_model",
    "rank_1_relevance",
    "rank_2_model",
    "rank_2_relevance",
    "rank_3_model",
    "rank_3_relevance",
]


def _nested_get(data: dict[str, Any], path: list[str], default: Any = "") -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def _first(values: Any) -> str:
    if isinstance(values, list):
        if not values:
            return ""
        return str(values[0])
    return "" if values is None else str(values)


def _candidate_to_row(
    requirement: dict[str, str],
    candidate: dict[str, Any],
    rank: int,
    kg_lookup: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    instance_name = candidate.get("instance_name") or _nested_get(candidate, ["kg_info", "instance_name"], "")
    kg_info = candidate.get("kg_info", {}) or {}
    if not kg_info and kg_lookup:
        kg_info = kg_lookup.get(instance_name, {}) or {}
    data_props = kg_info.get("data_properties", {}) or {}
    object_props = kg_info.get("object_properties", {}) or {}
    return {
        "Requirement ID": requirement["requirement_id"],
        "Requirement group": requirement["requirement_group"],
        "Requirement name": requirement["requirement_name"],
        "Requirement text": requirement["requirement_text"],
        "Top rank": rank,
        "Instance": instance_name or kg_info.get("instance_name", ""),
        "Model name": candidate.get("model_name") or _first(data_props.get("hasModelName")),
        "PDF file": _first(data_props.get("hasSourcePDFFileName"))
        or _first(data_props.get("hasSourceFileName"))
        or Path(_first(data_props.get("hasSourcePDFPath")) or _first(data_props.get("hasSourceFilePath"))).name,
        "Paper title": _first(data_props.get("hasPaperTitle")),
        "Final score": candidate.get("final_score", ""),
        "Recommendation reason": candidate.get("recommendation_reason", ""),
        "Matched needs": candidate.get("matched_needs", ""),
        "Strengths": candidate.get("strengths", ""),
        "Limitations": candidate.get("limitations", ""),
        "Simple explanation": candidate.get("simple_explanation", ""),
        "Objective text": _first(data_props.get("hasObjectiveFunction")),
        "Constraint text": _first(data_props.get("hasConstraintFunction")),
        "Parameter text": _first(data_props.get("usesParameter")),
        "Mathematical problem types": "; ".join(object_props.get("hasMathematicalProblemType", [])),
        "Technologies": "; ".join(object_props.get("hasModeledTechnology", [])),
        "Sectors": "; ".join(object_props.get("coversSector", [])),
    }


def flatten_validation2_result(
    requirement: dict[str, str],
    pipeline_result: dict[str, Any],
    final_top_n: int = 3,
) -> list[dict[str, Any]]:
    """Convert one pipeline output into table rows.

    A no-result row is kept so every requirement remains visible in the final
    validation table.
    """
    kg_lookup = {}
    for item in pipeline_result.get("top15_candidates", []) or []:
        kg_info = item.get("kg_info", {}) or {}
        instance_name = item.get("instance_name") or kg_info.get("instance_name", "")
        if instance_name:
            kg_lookup[instance_name] = kg_info

    top_candidates = pipeline_result.get("final_top3") or pipeline_result.get("top3") or []
    top_candidates = top_candidates[:final_top_n]
    if not top_candidates:
        return [
            {
                "Requirement ID": requirement["requirement_id"],
                "Requirement group": requirement["requirement_group"],
                "Requirement name": requirement["requirement_name"],
                "Requirement text": requirement["requirement_text"],
                "Top rank": "",
                "Instance": "No suitable PaperModel",
                "Model name": "No suitable PaperModel",
                "PDF file": "",
                "Paper title": "",
                "Final score": "",
                "Recommendation reason": "No candidate remained after the KG-backed recommendation pipeline.",
                "Matched needs": "",
                "Strengths": "",
                "Limitations": "",
                "Simple explanation": "",
                "Objective text": "",
                "Constraint text": "",
                "Parameter text": "",
                "Mathematical problem types": "",
                "Technologies": "",
                "Sectors": "",
            }
        ]
    rows = [
        _candidate_to_row(requirement, candidate, rank, kg_lookup=kg_lookup)
        for rank, candidate in enumerate(top_candidates, 1)
    ]
    for rank in range(len(rows) + 1, final_top_n + 1):
        rows.append(
            {
                "Requirement ID": requirement["requirement_id"],
                "Requirement group": requirement["requirement_group"],
                "Requirement name": requirement["requirement_name"],
                "Requirement text": requirement["requirement_text"],
                "Top rank": rank,
                "Instance": "No enough suitable PaperModel",
                "Model name": "No enough suitable PaperModel",
                "PDF file": "",
                "Paper title": "",
                "Final score": "",
                "Recommendation reason": "Fewer than three candidates passed grouped prefiltering and completed close reading.",
                "Matched needs": "",
                "Strengths": "",
                "Limitations": "No additional suitable PaperModel was available for this rank.",
                "Simple explanation": "",
                "Objective text": "",
                "Constraint text": "",
                "Parameter text": "",
                "Mathematical problem types": "",
                "Technologies": "",
                "Sectors": "",
            }
        )
    return rows


def run_validation2_single(requirement: dict[str, str], final_top_n: int = 3) -> dict[str, Any]:
    """Run the online recommendation pipeline for one validation requirement."""
    prompt_hash = current_online_recommendation_prompt_hash()
    log_buffer = io.StringIO()
    with contextlib.redirect_stdout(log_buffer):
        pipeline_result = run_direct_online_recommendation_pipeline(requirement["requirement_text"])
    rows = flatten_validation2_result(requirement, pipeline_result, final_top_n=final_top_n)
    return {
        "requirement": requirement,
        "prompt_hash": prompt_hash,
        "model": MODEL_NAME,
        "pipeline_result": pipeline_result,
        "top_rows": rows,
        "run_log": log_buffer.getvalue(),
    }


def run_validation2_batch(
    requirements: list[dict[str, str]] | None = None,
    final_top_n: int = 3,
    save: bool = True,
    resume: bool = True,
    stop_on_error: bool = True,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Run all Validation2.0 requirements and optionally save CSV/JSON output.

    Results are saved after every successfully processed requirement. This is
    intentional because the 54-case benchmark can hit API quota/rate limits; a
    later run can resume from the existing JSON instead of restarting from the
    first requirement. If no requirement has a current compatible result, an
    API failure leaves the last saved snapshot untouched instead of replacing
    it with empty CSV/JSON files.
    """
    selected_requirements = (
        USER_REQUIREMENTS if requirements is None else requirements
    )
    current_prompt_hash = current_online_recommendation_prompt_hash()
    VALIDATION2_TOP3_CSV.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION2_RAW_JSON.parent.mkdir(parents=True, exist_ok=True)

    raw_results: list[dict[str, Any]] = []
    if resume and VALIDATION2_RAW_JSON.exists():
        raw_results = load_validation2_raw_results() or []
        selected_by_id = {
            requirement["requirement_id"]: requirement
            for requirement in selected_requirements
        }
        loaded_count = len(raw_results)
        raw_results = [
            result
            for result in raw_results
            if isinstance(result, dict)
            and result.get("prompt_hash") == current_prompt_hash
            and result.get("model") == MODEL_NAME
            and result.get("requirement", {})
            == selected_by_id.get(
                _nested_get(result, ["requirement", "requirement_id"], "")
            )
        ]
        stale_count = loaded_count - len(raw_results)
        if stale_count:
            print(
                f"忽略 {stale_count} 条提示词或模型版本不一致的旧运行记录；"
                f"这些需求会重新调用 API。 / Ignored {stale_count} stale records "
                "whose prompt or model fingerprint differs; those requirements will rerun."
            )
        for result in raw_results:
            requirement = result.get("requirement", {})
            pipeline_result = result.get("pipeline_result", {})
            if requirement and pipeline_result:
                result["top_rows"] = flatten_validation2_result(
                    requirement,
                    pipeline_result,
                    final_top_n=final_top_n,
                )

    completed_ids = {
        _nested_get(result, ["requirement", "requirement_id"], "")
        for result in raw_results
        if isinstance(result, dict)
    }
    table_rows: list[dict[str, Any]] = []
    for result in raw_results:
        table_rows.extend(result.get("top_rows", []))

    for index, requirement in enumerate(selected_requirements, 1):
        requirement_id = requirement["requirement_id"]
        if requirement_id in completed_ids:
            print(
                f"[{index}/{len(selected_requirements)}] Skipping completed "
                f"{requirement_id} - {requirement['requirement_name']}"
            )
            continue
        print(
            f"[{index}/{len(selected_requirements)}] Running {requirement_id} - "
            f"{requirement['requirement_name']}"
        )
        try:
            result = run_validation2_single(requirement, final_top_n=final_top_n)
        except Exception as exc:
            if save and raw_results:
                save_validation2_results(pd.DataFrame(table_rows), raw_results)
            elif save:
                print(
                    "尚无新的成功结果，保留现有 Validation2 文件不覆盖。 / "
                    "No current result completed; existing Validation2 files were preserved."
                )
            print(
                f"Validation2.0 stopped at {requirement_id} - "
                f"{requirement['requirement_name']}: {type(exc).__name__}: {exc}"
            )
            if stop_on_error:
                raise
            continue
        raw_results.append(result)
        table_rows.extend(result["top_rows"])
        completed_ids.add(requirement_id)
        if save:
            save_validation2_results(pd.DataFrame(table_rows), raw_results)

    table = pd.DataFrame(table_rows)
    if save and raw_results:
        save_validation2_results(table, raw_results)
    elif save:
        print(
            "没有可保存的成功结果，保留现有 Validation2 文件不覆盖。 / "
            "No successful result to save; existing Validation2 files were preserved."
        )
    return table, raw_results


def save_validation2_results(table: pd.DataFrame, raw_results: list[dict[str, Any]]) -> None:
    """Atomically save the raw source-of-truth first, then its display table."""
    VALIDATION2_TOP3_CSV.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION2_RAW_JSON.parent.mkdir(parents=True, exist_ok=True)
    if table.empty and not list(table.columns):
        table = pd.DataFrame(columns=VALIDATION2_TABLE_COLUMNS)

    top3_temp_path: Path | None = None
    raw_temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            newline="",
            delete=False,
            dir=VALIDATION2_TOP3_CSV.parent,
            prefix=f".{VALIDATION2_TOP3_CSV.name}.",
            suffix=".tmp",
        ) as top3_temp:
            table.to_csv(top3_temp, index=False)
            top3_temp_path = Path(top3_temp.name)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=VALIDATION2_RAW_JSON.parent,
            prefix=f".{VALIDATION2_RAW_JSON.name}.",
            suffix=".tmp",
        ) as raw_temp:
            json.dump(
                make_project_paths_portable(raw_results),
                raw_temp,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
            raw_temp_path = Path(raw_temp.name)

        # Raw JSON is the rebuildable source of truth. Replace it first; the
        # derived CSV can always be rebuilt if the second replace is interrupted.
        raw_temp_path.replace(VALIDATION2_RAW_JSON)
        raw_temp_path = None
        top3_temp_path.replace(VALIDATION2_TOP3_CSV)
        top3_temp_path = None
    finally:
        if raw_temp_path is not None:
            raw_temp_path.unlink(missing_ok=True)
        if top3_temp_path is not None:
            top3_temp_path.unlink(missing_ok=True)


def load_validation2_top3_table() -> pd.DataFrame | None:
    if not VALIDATION2_TOP3_CSV.exists():
        return None
    return pd.read_csv(VALIDATION2_TOP3_CSV)


def load_validation2_raw_results() -> list[dict[str, Any]] | None:
    if not VALIDATION2_RAW_JSON.exists():
        return None
    return json.loads(VALIDATION2_RAW_JSON.read_text(encoding="utf-8"))


def rebuild_validation2_table_from_raw(
    raw_results: list[dict[str, Any]] | None = None,
    final_top_n: int = 3,
    save: bool = True,
) -> pd.DataFrame:
    """Rebuild the display CSV from saved raw pipeline results without LLM calls."""
    raw_results = raw_results if raw_results is not None else (load_validation2_raw_results() or [])
    table_rows: list[dict[str, Any]] = []
    for result in raw_results:
        requirement = result.get("requirement", {})
        pipeline_result = result.get("pipeline_result", {})
        table_rows.extend(flatten_validation2_result(requirement, pipeline_result, final_top_n=final_top_n))
    table = pd.DataFrame(table_rows)
    if save:
        save_validation2_results(table, raw_results)
    return table


def _clean_instance_name(value: Any) -> str:
    value = "" if value is None else str(value).strip()
    if value.lower() == "nan":
        return ""
    return value


def load_recommendation_human_gold_table(
    path: Path = RECOMMENDATION_HUMAN_GOLD_CSV,
) -> pd.DataFrame:
    """Load and strictly validate the single 54-requirement human Gold table."""
    if not path.exists():
        raise FileNotFoundError(
            f"Recommendation human Gold CSV is missing / 推荐人工 Gold CSV 不存在: {path}"
        )
    table = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if list(table.columns) != RECOMMENDATION_HUMAN_GOLD_COLUMNS:
        raise ValueError(
            "Recommendation human Gold CSV columns are invalid / 推荐人工 Gold CSV 列结构错误。"
            f"expected={RECOMMENDATION_HUMAN_GOLD_COLUMNS}, actual={list(table.columns)}, path={path}"
        )
    expected_ids = [requirement["requirement_id"] for requirement in USER_REQUIREMENTS]
    actual_ids = table["requirement_id"].tolist()
    if actual_ids != expected_ids:
        raise ValueError(
            "Recommendation human Gold must contain the canonical 54 requirements in order / "
            f"推荐人工 Gold 必须按权威顺序包含 54 条需求。expected={expected_ids}, actual={actual_ids}"
        )
    requirements_by_id = {
        requirement["requirement_id"]: requirement for requirement in USER_REQUIREMENTS
    }
    for _, row in table.iterrows():
        requirement_id = row["requirement_id"]
        canonical = requirements_by_id[requirement_id]
        for field in ("requirement_group", "requirement_name", "requirement_text"):
            if row[field] != canonical[field]:
                raise ValueError(
                    f"Human Gold {field} differs from canonical requirement / "
                    f"人工 Gold 与权威需求字段不一致: {requirement_id}, field={field}"
                )
        count_text = row["gold_model_count"].strip()
        if not count_text.isdigit():
            raise ValueError(
                f"Gold model count must be an integer / Gold 模型数量必须是整数: {requirement_id}"
            )
        model_count = int(count_text)
        acceptable_models = [_clean_instance_name(row[column]) for column in GOLD_ACCEPTABLE_MODEL_COLUMNS]
        ranked_models = [_clean_instance_name(row[column]) for column in GOLD_RANK_MODEL_COLUMNS]
        relevance_texts = [str(row[column]).strip() for column in GOLD_RANK_RELEVANCE_COLUMNS]
        if requirement_id.startswith("R"):
            if row["gold_standard_type"] != "unordered_acceptable_set" or row["evaluation_metric"] != "enterprise_candidate_top3_accuracy":
                raise ValueError(f"Enterprise Gold type or metric is invalid / 企业 Gold 类型或指标无效: {requirement_id}")
            if not 1 <= model_count <= len(GOLD_ACCEPTABLE_MODEL_COLUMNS):
                raise ValueError(f"Enterprise Gold model count is invalid / 企业 Gold 模型数无效: {requirement_id}")
            used_models = acceptable_models[:model_count]
            if any(not model for model in used_models) or any(acceptable_models[model_count:]):
                raise ValueError(f"Enterprise Gold model slots are not contiguous / 企业 Gold 模型槽位不连续: {requirement_id}")
            if any(ranked_models) or any(relevance_texts):
                raise ValueError(f"Enterprise Gold must not populate ranking columns / 企业 Gold 不得填写排名列: {requirement_id}")
        else:
            if row["gold_standard_type"] != "ordered_relevance_ranking" or row["evaluation_metric"] != "ndcg_at_3":
                raise ValueError(f"Motivation Gold type or metric is invalid / Motivation Gold 类型或指标无效: {requirement_id}")
            if not 1 <= model_count <= len(GOLD_RANK_MODEL_COLUMNS):
                raise ValueError(f"Motivation Gold model count is invalid / Motivation Gold 模型数无效: {requirement_id}")
            if any(acceptable_models):
                raise ValueError(f"Motivation Gold must not populate acceptable-set columns / Motivation Gold 不得填写候选集合列: {requirement_id}")
            used_models = ranked_models[:model_count]
            used_relevance_texts = relevance_texts[:model_count]
            if any(not model for model in used_models) or any(ranked_models[model_count:]):
                raise ValueError(f"Motivation Gold ranking slots are not contiguous / Motivation Gold 排名槽位不连续: {requirement_id}")
            if any(not value for value in used_relevance_texts) or any(relevance_texts[model_count:]):
                raise ValueError(f"Motivation Gold relevance slots are not contiguous / Motivation Gold 相关性槽位不连续: {requirement_id}")
            try:
                relevances = [float(value) for value in used_relevance_texts]
            except ValueError as exc:
                raise ValueError(f"Motivation Gold relevance must be numeric / Motivation Gold 相关性必须为数字: {requirement_id}") from exc
            if any(not math.isfinite(value) or value < 0 for value in relevances):
                raise ValueError(f"Motivation Gold relevance must be finite and non-negative / Motivation Gold 相关性必须为有限非负数: {requirement_id}")
            if not any(relevances) or relevances != sorted(relevances, reverse=True):
                raise ValueError(f"Motivation Gold relevance must be positive and non-increasing / Motivation Gold 相关性必须为正且非递增: {requirement_id}")
        if len(used_models) != len(set(used_models)):
            raise ValueError(f"Gold models must be unique within each requirement / 同一需求内 Gold 模型不得重复: {requirement_id}")
    return table


def load_enterprise_gold_candidates(
    gold_table: pd.DataFrame | None = None,
) -> dict[str, set[str]]:
    """Derive the 19 unordered enterprise candidate sets from the unified Gold table."""
    table = gold_table if gold_table is not None else load_recommendation_human_gold_table()
    gold: dict[str, set[str]] = {}
    for _, row in table[table["requirement_id"].str.startswith("R")].iterrows():
        model_count = int(row["gold_model_count"])
        gold[row["requirement_id"]] = {
            _clean_instance_name(row[f"acceptable_model_{index}"])
            for index in range(1, model_count + 1)
        }
    return gold


def load_motivation_gold_rankings(
    gold_table: pd.DataFrame | None = None,
) -> dict[str, list[str]]:
    """Derive the 35 ordered Motivation rankings from the unified Gold table."""
    table = gold_table if gold_table is not None else load_recommendation_human_gold_table()
    rankings: dict[str, list[str]] = {}
    for _, row in table[table["requirement_id"].str.startswith("M")].iterrows():
        model_count = int(row["gold_model_count"])
        rankings[row["requirement_id"]] = [
            _clean_instance_name(row[f"rank_{rank}_model"])
            for rank in range(1, model_count + 1)
        ]
    return rankings


def load_motivation_gold_relevance(
    gold_table: pd.DataFrame | None = None,
) -> dict[str, dict[str, float]]:
    """Derive per-model nDCG relevance directly from the unified Gold table."""
    table = gold_table if gold_table is not None else load_recommendation_human_gold_table()
    relevance_by_requirement: dict[str, dict[str, float]] = {}
    for _, row in table[table["requirement_id"].str.startswith("M")].iterrows():
        model_count = int(row["gold_model_count"])
        relevance_by_requirement[row["requirement_id"]] = {
            _clean_instance_name(row[f"rank_{rank}_model"]): float(row[f"rank_{rank}_relevance"])
            for rank in range(1, model_count + 1)
        }
    return relevance_by_requirement


def build_enterprise_gold_table(gold: dict[str, set[str]] | None = None) -> pd.DataFrame:
    gold = gold if gold is not None else load_enterprise_gold_candidates()
    rows = []
    for requirement in USER_REQUIREMENTS:
        if not requirement["requirement_id"].startswith("R"):
            continue
        requirement_id = requirement["requirement_id"]
        for instance_name in sorted(gold.get(requirement_id, set())):
            rows.append(
                {
                    "Requirement ID": requirement_id,
                    "Requirement name": requirement["requirement_name"],
                    "Gold acceptable instance": instance_name,
                }
            )
    return pd.DataFrame(rows)


def build_motivation_gold_table(
    gold_table: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Expand the Motivation rows into the legacy 68-row human-readable view."""
    columns = [
        "Requirement ID",
        "Requirement name",
        "Gold rank",
        "Gold instance",
        "Relevance",
    ]
    table = gold_table if gold_table is not None else load_recommendation_human_gold_table()
    rows = []
    for _, row in table[table["requirement_id"].str.startswith("M")].iterrows():
        for rank in range(1, int(row["gold_model_count"]) + 1):
            rows.append(
                {
                    "Requirement ID": row["requirement_id"],
                    "Requirement name": row["requirement_name"],
                    "Gold rank": rank,
                    "Gold instance": row[f"rank_{rank}_model"],
                    "Relevance": float(row[f"rank_{rank}_relevance"]),
                }
            )
    return pd.DataFrame(rows, columns=columns)


def _predicted_instances_for_requirement(top3_table: pd.DataFrame, requirement_id: str) -> list[str]:
    subset = top3_table[top3_table["Requirement ID"] == requirement_id].copy()
    if "Top rank" in subset.columns:
        subset = subset.sort_values("Top rank")
    instances = []
    for value in subset.get("Instance", []):
        instance_name = _clean_instance_name(value)
        if instance_name and instance_name != "No enough suitable PaperModel":
            instances.append(instance_name)
    return instances[:3]


def _ndcg_at_3(
    predicted: list[str],
    relevance: dict[str, float],
) -> tuple[float, float, float]:
    dcg = 0.0
    for rank, instance_name in enumerate(predicted[:3], 1):
        rel = relevance.get(instance_name, 0.0)
        dcg += rel / math.log2(rank + 1)
    ideal_relevances = sorted(relevance.values(), reverse=True)[:3]
    idcg = sum(rel / math.log2(rank + 1) for rank, rel in enumerate(ideal_relevances, 1))
    ndcg = dcg / idcg if idcg else 0.0
    return dcg, idcg, ndcg


def evaluate_validation2_accuracy(
    top3_table: pd.DataFrame | None = None,
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate Validation2.0 recommendations against human gold answers.

    Enterprise requirements use set-based Top-3 hit rate.
    Motivation requirements use ordered nDCG@3 with relevance read from the
    unified human Gold CSV.
    """
    if top3_table is None:
        top3_table = load_validation2_top3_table()
    if top3_table is None or top3_table.empty:
        top3_table = pd.DataFrame(columns=VALIDATION2_TABLE_COLUMNS)

    human_gold_table = load_recommendation_human_gold_table()
    enterprise_gold = load_enterprise_gold_candidates(human_gold_table)
    motivation_gold = load_motivation_gold_rankings(human_gold_table)
    motivation_relevance = load_motivation_gold_relevance(human_gold_table)
    rows = []

    for requirement in USER_REQUIREMENTS:
        requirement_id = requirement["requirement_id"]
        predicted = _predicted_instances_for_requirement(top3_table, requirement_id)
        if requirement_id.startswith("R"):
            gold_set = enterprise_gold.get(requirement_id, set())
            hit_count = sum(1 for instance_name in predicted if instance_name in gold_set)
            score = hit_count / 3.0 if gold_set else 0.0
            rows.append(
                {
                    "Requirement ID": requirement_id,
                    "Requirement type": "Enterprise candidate set",
                    "Requirement name": requirement["requirement_name"],
                    "Predicted Top3": " | ".join(predicted),
                    "Gold answer": " | ".join(sorted(gold_set)),
                    "Metric": "Enterprise Requirements Candidate Top-3 Accuracy",
                    "Hit count": hit_count,
                    "DCG": "",
                    "IDCG": "",
                    "Score": score,
                    "Score (%)": score * 100,
                    "Explanation": "Top3 hit count divided by 3.",
                }
            )
        else:
            gold_ranking = motivation_gold.get(requirement_id, [])
            dcg, idcg, ndcg = _ndcg_at_3(
                predicted,
                motivation_relevance.get(requirement_id, {}),
            )
            rows.append(
                {
                    "Requirement ID": requirement_id,
                    "Requirement type": "Motivation ordered ranking",
                    "Requirement name": requirement["requirement_name"],
                    "Predicted Top3": " | ".join(predicted),
                    "Gold answer": " | ".join(gold_ranking),
                    "Metric": "nDCG@3",
                    "Hit count": sum(1 for instance_name in predicted if instance_name in set(gold_ranking)),
                    "DCG": dcg,
                    "IDCG": idcg,
                    "Score": ndcg,
                    "Score (%)": ndcg * 100,
                    "Explanation": "nDCG@3 with per-rank relevance read from the unified human Gold CSV.",
                }
            )

    accuracy_table = pd.DataFrame(rows)
    enterprise_scores = accuracy_table[accuracy_table["Requirement type"] == "Enterprise candidate set"]["Score"]
    motivation_scores = accuracy_table[accuracy_table["Requirement type"] == "Motivation ordered ranking"]["Score"]
    summary_rows = [
        {
            "Metric": "Enterprise Requirements Candidate Top-3 Accuracy",
            "Requirement count": int(enterprise_scores.count()),
            "Average score": float(enterprise_scores.mean()) if not enterprise_scores.empty else 0.0,
            "Average score (%)": float(enterprise_scores.mean() * 100) if not enterprise_scores.empty else 0.0,
            "Meaning": "Average share of recommended Top3 models that belong to the human acceptable candidate set.",
        },
        {
            "Metric": "Motivation nDCG@3",
            "Requirement count": int(motivation_scores.count()),
            "Average score": float(motivation_scores.mean()) if not motivation_scores.empty else 0.0,
            "Average score (%)": float(motivation_scores.mean() * 100) if not motivation_scores.empty else 0.0,
            "Meaning": "Average nDCG@3 over all canonical motivation requirements.",
        },
    ]
    summary_table = pd.DataFrame(summary_rows)
    enterprise_gold_table = build_enterprise_gold_table(enterprise_gold)
    motivation_gold_table = build_motivation_gold_table(human_gold_table)

    if save:
        VALIDATION2_METRICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        accuracy_table.to_csv(VALIDATION2_ACCURACY_BY_REQUIREMENT_CSV, index=False, encoding="utf-8-sig")
        summary_table.to_csv(VALIDATION2_ACCURACY_SUMMARY_CSV, index=False, encoding="utf-8-sig")

    return accuracy_table, summary_table, enterprise_gold_table, motivation_gold_table
