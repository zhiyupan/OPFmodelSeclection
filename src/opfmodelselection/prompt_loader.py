"""Load and render the root-level LLM prompt catalog.

The catalog is intentionally read on every call so an edit to ``prompts.toml``
takes effect on the next API request without restarting a notebook or GUI.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib

from .config import PROMPT_CATALOG_PATH

_PLACEHOLDER_RE = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")

REQUIRED_PROMPT_PLACEHOLDERS = {
    "common.soft_schema_instruction": {"schema_json"},
    "paper_processing.llm_payload.user": {
        "paper_name",
        "paper_path",
        "paper_text",
        "table_summaries",
        "image_summaries",
    },
    "paper_extraction.metadata.system": set(),
    "paper_extraction.metadata.user": {"paper_text"},
    "paper_extraction.structure.system": set(),
    "paper_extraction.structure.user": {
        "objective_level2_map",
        "constraint_level2_map",
        "parameter_level2_map",
        "object_feature_text",
        "paper_text",
    },
    "paper_extraction.review.system": set(),
    "paper_extraction.review.user": {"current_result_json", "paper_text"},
    "online_recommendation.prefilter.system": set(),
    "online_recommendation.prefilter.user": {
        "user_requirement_text",
        "group_index",
        "total_groups",
        "candidate_payload_json",
    },
    "online_recommendation.prefilter.retry_invalid_json": set(),
    "online_recommendation.prefilter_schema_descriptions.instance_name": set(),
    "online_recommendation.prefilter_schema_descriptions.prefilter_score": set(),
    "online_recommendation.prefilter_schema_descriptions.why_matched": set(),
    "online_recommendation.prefilter_schema_descriptions.main_risk_or_gap": set(),
    "online_recommendation.prefilter_schema_descriptions.supporting_evidence": set(),
    "online_recommendation.close_reading.system": set(),
    "online_recommendation.close_reading.user": {
        "user_requirement_text",
        "display_candidates_json",
        "expected_count",
        "expected_names_json",
    },
    "paper_lookup.translation.system": set(),
    "paper_lookup.translation.user": {"unique_values_json"},
    "semantic_evaluation.gold_translation.system": set(),
    "semantic_evaluation.gold_translation.user": {"fields_to_translate_json"},
    "semantic_evaluation.factual_judgment.system": set(),
    "semantic_evaluation.factual_judgment.user": {"field_payload_json"},
}


def _lookup_prompt(catalog: dict, prompt_id: str) -> str:
    value = catalog
    for part in prompt_id.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"Prompt not found / 未找到提示词: {prompt_id}")
        value = value[part]
    if not isinstance(value, str):
        raise TypeError(f"Prompt is not text / 提示词不是文本: {prompt_id}")
    return value.strip()


def load_prompt_catalog() -> dict:
    """Read and parse the current root prompt catalog."""
    if not PROMPT_CATALOG_PATH.exists():
        raise FileNotFoundError(
            "Root prompt catalog is missing / 根目录提示词文件不存在: "
            f"{PROMPT_CATALOG_PATH}"
        )
    with PROMPT_CATALOG_PATH.open("rb") as handle:
        catalog = tomllib.load(handle)
    if catalog.get("version") != 1:
        raise ValueError(
            "Unsupported prompts.toml version / 不支持的提示词版本: "
            f"{catalog.get('version')!r}"
        )
    for prompt_id, expected_placeholders in REQUIRED_PROMPT_PLACEHOLDERS.items():
        prompt = _lookup_prompt(catalog, prompt_id)
        actual_placeholders = set(_PLACEHOLDER_RE.findall(prompt))
        if actual_placeholders != expected_placeholders:
            raise ValueError(
                f"Prompt placeholders changed for {prompt_id} / 提示词占位符不匹配: "
                f"expected={sorted(expected_placeholders)}, actual={sorted(actual_placeholders)}"
            )
    return catalog


def get_prompt(prompt_id: str) -> str:
    """Return one prompt by dotted path, for example ``common.soft_schema_instruction``."""
    return _lookup_prompt(load_prompt_catalog(), prompt_id)


def render_prompt(prompt_id: str, **values) -> str:
    """Render ``{{placeholder}}`` values in a prompt loaded from disk."""
    template = get_prompt(prompt_id)
    required = set(_PLACEHOLDER_RE.findall(template))
    missing = sorted(required.difference(values))
    if missing:
        raise KeyError(
            f"Missing prompt values for {prompt_id} / 提示词缺少变量: "
            + ", ".join(missing)
        )

    def replace(match: re.Match) -> str:
        return str(values[match.group(1)])

    return _PLACEHOLDER_RE.sub(replace, template)


def prompt_fingerprint(*prompt_ids: str) -> str:
    """Return a stable hash used to invalidate LLM caches after prompt edits."""
    payload = {prompt_id: get_prompt(prompt_id) for prompt_id in prompt_ids}
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
