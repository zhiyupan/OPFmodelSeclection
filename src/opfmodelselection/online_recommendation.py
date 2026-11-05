"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *
from .prompt_loader import get_prompt, render_prompt

# 9.1 Define direct online recommendation functions for user requirements.

import re
import json
import math
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

ONLINE_PREFILTER_GROUP_SIZE = 12
ONLINE_PREFILTER_MIN_SCORE = 65
ONLINE_FINAL_TOP_N = 3
ONLINE_CLOSE_READING_MAX_FULL_ATTEMPTS = 2

ONLINE_RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
ONLINE_RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"


def online_local_name(resource):
    """Return local name from #Name, OPF full IRI, or generic IRI."""
    if not resource:
        return ""
    value = str(resource)
    if value.startswith("#"):
        return value[1:]
    if "OPF_IRI" in globals() and value.startswith(OPF_IRI):
        return value[len(OPF_IRI):]
    if "#" in value:
        return value.rsplit("#", 1)[-1]
    return value.rstrip("/").rsplit("/", 1)[-1]


def online_class_labels_from_owl(root):
    """Read retained OPF/OEO rdfs:label values so external class links stay readable."""
    labels = {}
    label_tag = "{http://www.w3.org/2000/01/rdf-schema#}label"
    for elem in root.iter():
        if not elem.tag.endswith("}Class"):
            continue
        iri = elem.attrib.get(ONLINE_RDF_ABOUT, "")
        label_elem = elem.find(label_tag)
        if iri and label_elem is not None and (label_elem.text or "").strip():
            labels[online_local_name(iri)] = label_elem.text.strip()
    return labels


def online_class_labels_from_paths(*paths):
    labels = {}
    for path in paths:
        if not path or not Path(path).exists():
            continue
        root = ET.fromstring(Path(path).read_text(encoding="utf-8"))
        labels.update(online_class_labels_from_owl(root))
    return labels


def online_readable_object_target(resource, labels):
    """Keep exact object target id and append a retained label when available."""
    target = online_local_name(resource)
    label = labels.get(target)
    return f"{target} | {label}" if label and label != target else target


def online_element_local_tag(element):
    return element.tag.split("}", 1)[-1] if "}" in element.tag else element.tag


def online_is_opfmodel_individual(individual_element):
    for child in individual_element:
        if online_element_local_tag(child) == "type":
            if online_local_name(child.attrib.get(ONLINE_RDF_RESOURCE)) == "OPFModel":
                return True
    return False


def resolve_online_instance_owl_path(owl_path=INSTANCE_OWL_PATH):
    """Resolve an OWL file that actually contains PaperModel individuals."""
    candidates = [Path(owl_path), INSTANCE_OWL_PATH]
    seen = set()
    checked = []
    for candidate in candidates:
        candidate = Path(candidate)
        if candidate in seen:
            continue
        seen.add(candidate)
        checked.append(str(candidate))
        if not candidate.exists():
            continue
        try:
            root = ET.fromstring(candidate.read_text(encoding="utf-8"))
        except (OSError, ET.ParseError):
            continue
        if any(
            online_element_local_tag(element) == "NamedIndividual"
            and online_is_opfmodel_individual(element)
            for element in root.iter()
        ):
            return candidate
    raise FileNotFoundError(
        "No readable OWL containing PaperModel individuals was found. Tried: "
        + ", ".join(checked)
    )


def read_all_paper_model_instances(owl_path=INSTANCE_OWL_PATH, schema_path=BASE_OWL_PATH):
    """Read all OPFModel / PaperModel individuals from OWL XML."""
    read_path = resolve_online_instance_owl_path(owl_path)
    root = ET.fromstring(read_path.read_text(encoding="utf-8"))
    labels = online_class_labels_from_paths(schema_path, read_path)
    records = []
    for individual in root.iter():
        if not individual.tag.endswith("}NamedIndividual"):
            continue
        if not online_is_opfmodel_individual(individual):
            continue

        iri = individual.attrib.get(ONLINE_RDF_ABOUT, "")
        instance_name = online_local_name(iri)
        data_properties = {}
        object_properties = {}

        for child in individual:
            prop = online_element_local_tag(child)
            if prop == "type":
                continue
            target = child.attrib.get(ONLINE_RDF_RESOURCE)
            if target:
                object_properties.setdefault(prop, []).append(online_readable_object_target(target, labels))
            else:
                text = (child.text or "").strip()
                if text:
                    data_properties.setdefault(prop, []).append(text)

        records.append(
            {
                "instance_name": instance_name,
                "iri": iri,
                "data_properties": data_properties,
                "object_properties": object_properties,
            }
        )

    records.sort(key=lambda r: (r["data_properties"].get("hasPaperTitle", [""])[0].lower(), r["instance_name"].lower()))
    return records


def first_value(values, default=""):
    if isinstance(values, list):
        return values[0] if values else default
    return values if values is not None else default


def join_values(values, max_items=12):
    if not values:
        return ""
    if not isinstance(values, list):
        values = [values]
    values = [str(v) for v in values if str(v).strip()]
    if len(values) > max_items:
        return "; ".join(values[:max_items]) + f"; ... (+{len(values) - max_items})"
    return "; ".join(values)


def compact_text(text, max_chars=900):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


ONLINE_KEY_DATA_FIELDS = [
    "hasModelName",
    "hasPaperTitle",
    "hasPublicationYear",
    "hasDOI",
    "hasAuthor",
    "hasInstitution",
    "hasPrimaryPurpose",
    "hasMotivation",
    "hasSolvedProblem",
    "hasResearchQuestion",
    "hasPrimaryOutput",
    "hasModelFeature",
    "hasPowerFlowFormulationFeature",
    "hasTimeHorizonFeature",
    "hasTemporalResolution",
    "hasOptimizationHorizon",
    "hasUncertaintyHandlingFeature",
    "hasPowerSystemDomainFeature",
    "hasSolutionMethodEnhancementFeature",
    "hasModelPerformanceFeature",
    "hasDemandSideFeature",
    "hasObjectiveFunction",
    "hasConstraintFunction",
    "usesParameter",
    "hasMathematicalProblemType",
    "hasSolutionDetailsSummary",
    "hasModelValidationSummary",
    "hasFindingsSummary",
    "hasStrengthsAndLimitationsSummary",
    "isScenarioSuitability",
    "hasFurtherProperty",
]


def compact_paper_model_for_llm(record, include_all=False):
    """Build compact KG info package for one PaperModel instance."""
    data = record.get("data_properties", {})
    objects = record.get("object_properties", {})
    compact = {
        "instance_name": record["instance_name"],
        "metadata": {
            "hasModelName": join_values(data.get("hasModelName")),
            "hasPaperTitle": join_values(data.get("hasPaperTitle")),
            "hasPublicationYear": join_values(data.get("hasPublicationYear")),
            "hasDOI": join_values(data.get("hasDOI")),
            "hasAuthor": join_values(data.get("hasAuthor"), max_items=5),
            "hasInstitution": join_values(data.get("hasInstitution"), max_items=5),
        },
        "data_properties": {},
        "object_properties": objects,
    }
    for field in ONLINE_KEY_DATA_FIELDS:
        if field in data:
            compact["data_properties"][field] = compact_text(join_values(data[field], max_items=20), max_chars=1200 if include_all else 650)
    if include_all:
        for field, values in data.items():
            if field not in compact["data_properties"]:
                compact["data_properties"][field] = compact_text(join_values(values, max_items=20), max_chars=1000)
    return compact


def chunk_list(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def parse_json_object_from_text(text):
    """Parse a JSON object from hard-schema or soft-prompt model output."""
    if isinstance(text, dict):
        return text
    text = str(text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def build_prefilter_schema(candidate_instance_names):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "selected_candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "instance_name": {
                            "type": "string",
                            "enum": candidate_instance_names,
                            "description": get_prompt(
                                "online_recommendation.prefilter_schema_descriptions.instance_name"
                            ),
                        },
                        "prefilter_score": {
                            "type": "number",
                            "description": get_prompt(
                                "online_recommendation.prefilter_schema_descriptions.prefilter_score"
                            ),
                        },
                        "why_matched": {
                            "type": "string",
                            "description": get_prompt(
                                "online_recommendation.prefilter_schema_descriptions.why_matched"
                            ),
                        },
                        "main_risk_or_gap": {
                            "type": "string",
                            "description": get_prompt(
                                "online_recommendation.prefilter_schema_descriptions.main_risk_or_gap"
                            ),
                        },
                        "supporting_evidence": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": get_prompt(
                                "online_recommendation.prefilter_schema_descriptions.supporting_evidence"
                            ),
                        },
                    },
                    "required": [
                        "instance_name",
                        "prefilter_score",
                        "why_matched",
                        "main_risk_or_gap",
                        "supporting_evidence",
                    ],
                },
            },
            "group_summary": {"type": "string"},
        },
        "required": ["selected_candidates", "group_summary"],
    }


def openai_json_schema_response_format(name, schema):
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": True,
            "schema": schema,
        },
    }


def build_prefilter_messages(user_requirement_text, candidate_group, group_index, total_groups):
    candidate_payload = [compact_paper_model_for_llm(record, include_all=True) for record in candidate_group]
    system_prompt = render_prompt("online_recommendation.prefilter.system")
    user_prompt = render_prompt(
        "online_recommendation.prefilter.user",
        user_requirement_text=user_requirement_text,
        group_index=group_index,
        total_groups=total_groups,
        candidate_payload_json=json.dumps(
            candidate_payload,
            ensure_ascii=False,
            indent=2,
        ),
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def call_prefilter_group(user_requirement_text, candidate_group, group_index, total_groups):
    names = [record["instance_name"] for record in candidate_group]
    messages = build_prefilter_messages(user_requirement_text, candidate_group, group_index, total_groups)
    schema = build_prefilter_schema(names)

    if USE_OPENAI_HARD_SCHEMA:
        if openai_client is None:
            raise RuntimeError("缺少 OPENAI_API_KEY / Missing OPENAI_API_KEY.")
        last_error = None
        current_messages = list(messages)
        for attempt in range(1, 4):
            check_llm_input_budget(
                current_messages,
                model_name=OPENAI_MODEL_NAME,
                call_name=f"online_prefilter_group_{group_index}_attempt_{attempt}",
            )
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL_NAME,
                temperature=LLM_API_TEMPERATURE,
                messages=current_messages,
                response_format=openai_json_schema_response_format(f"opf_prefilter_group_{group_index}", schema),
                timeout=180,
            )
            content = response.choices[0].message.content or ""
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:
                last_error = exc
                current_messages = messages + [
                    {
                        "role": "user",
                        "content": render_prompt(
                            "online_recommendation.prefilter.retry_invalid_json"
                        ),
                    }
                ]
        raise last_error

    if rwth_client is None:
        raise RuntimeError("缺少 RWTH_API_KEY / Missing RWTH_API_KEY.")
    soft_messages = messages + [
        {
            "role": "user",
            "content": render_prompt(
                "common.soft_schema_instruction",
                schema_json=json.dumps(schema, ensure_ascii=False, indent=2),
            ),
        }
    ]
    check_llm_input_budget(
        soft_messages,
        model_name=RWTH_MODEL_NAME,
        call_name=f"online_prefilter_group_{group_index}_rwth",
    )
    response = rwth_client.chat.completions.create(
        model=RWTH_MODEL_NAME,
        temperature=LLM_API_TEMPERATURE,
        messages=soft_messages,
        timeout=180,
    )
    return parse_json_object_from_text(response.choices[0].message.content)


def validate_prefilter_output(raw_output, candidate_group):
    allowed = {record["instance_name"] for record in candidate_group}
    valid = []
    for item in raw_output.get("selected_candidates", []) or []:
        name = item.get("instance_name")
        if name not in allowed:
            continue
        try:
            score = float(item.get("prefilter_score", 0))
        except Exception:
            score = 0
        if score < ONLINE_PREFILTER_MIN_SCORE:
            continue
        valid.append(
            {
                "instance_name": name,
                "prefilter_score": score,
                "why_matched": str(item.get("why_matched", "")).strip(),
                "main_risk_or_gap": str(item.get("main_risk_or_gap", "")).strip(),
                "supporting_evidence": [str(x).strip() for x in item.get("supporting_evidence", []) if str(x).strip()],
            }
        )
    valid.sort(key=lambda x: x["prefilter_score"], reverse=True)
    return {"selected_candidates": valid, "group_summary": raw_output.get("group_summary", "")}


def run_llm_grouped_prefilter(user_requirement_text, group_size=ONLINE_PREFILTER_GROUP_SIZE):
    read_path = resolve_online_instance_owl_path(INSTANCE_OWL_PATH)
    print("知识图谱 读取路径 / Knowledge graph read path:", read_path)
    records = read_all_paper_model_instances(read_path)
    if not records:
        raise RuntimeError("OWL 中没有 OPFModel / PaperModel 实例 / No OPFModel instances found.")

    groups = list(chunk_list(records, group_size))
    merged = {}
    group_outputs = []

    print("用户原始需求 / User requirement:")
    print(user_requirement_text)
    print("\nPaperModel 实例数量 / PaperModel count:", len(records))
    print("LLM 初筛分组大小 / Group size:", group_size)
    print("LLM 初筛组数 / Group count:", len(groups))

    for index, group in enumerate(groups, start=1):
        print(f"\n运行 LLM 初筛组 / Running prefilter group {index}/{len(groups)}")
        raw = call_prefilter_group(user_requirement_text, group, index, len(groups))
        validated = validate_prefilter_output(raw, group)
        group_outputs.append({"group_index": index, "raw_output": raw, "validated_output": validated})
        for candidate in validated["selected_candidates"]:
            name = candidate["instance_name"]
            if name not in merged or candidate["prefilter_score"] > merged[name]["prefilter_score"]:
                merged[name] = candidate
        print("本组通过候选数 / Passed in this group:", len(validated["selected_candidates"]))

    selected = sorted(merged.values(), key=lambda x: x["prefilter_score"], reverse=True)
    result = {
        "user_requirement": user_requirement_text,
        "group_size": group_size,
        "min_score": ONLINE_PREFILTER_MIN_SCORE,
        "selected_candidates": selected,
        "group_outputs": group_outputs,
    }

    print("\n合并后的初筛候选 / Merged prefilter candidates:")
    for rank, item in enumerate(selected, start=1):
        print(f"{rank}. {item['instance_name']} | score={item['prefilter_score']}")
        print("   why:", item["why_matched"])
        print("   risk:", item["main_risk_or_gap"])
    return result


def build_close_reading_candidates_from_prefilter(prefilter_result):
    """Attach complete PaperModel records to every candidate that passed prefilter."""
    selected = prefilter_result.get("selected_candidates", []) or []
    selected = sorted(selected, key=lambda x: x.get("prefilter_score", 0), reverse=True)
    all_records = {record["instance_name"]: record for record in read_all_paper_model_instances(INSTANCE_OWL_PATH)}
    candidates = []
    for item in selected:
        record = all_records.get(item["instance_name"])
        if not record:
            continue
        candidates.append(
            {
                "evidence_package": item,
                "kg_info": compact_paper_model_for_llm(record, include_all=True),
            }
        )
    return candidates


def build_close_reading_schema(candidate_instance_names):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "ranked_candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "rank": {"type": "integer"},
                        "instance_name": {"type": "string", "enum": candidate_instance_names},
                        "final_score": {"type": "number"},
                        "recommendation_reason": {"type": "string"},
                        "matched_needs": {"type": "string"},
                        "strengths": {"type": "string"},
                        "limitations": {"type": "string"},
                        "simple_model_explanation": {"type": "string"},
                    },
                    "required": [
                        "rank",
                        "instance_name",
                        "final_score",
                        "recommendation_reason",
                        "matched_needs",
                        "strengths",
                        "limitations",
                        "simple_model_explanation",
                    ],
                },
            },
            "overall_summary": {"type": "string"},
        },
        "required": ["ranked_candidates", "overall_summary"],
    }


def build_close_reading_messages(user_requirement_text, top_candidates):
    display_candidates = [candidate.get("kg_info", {}) for candidate in top_candidates]
    expected_names = [candidate.get("kg_info", {}).get("instance_name", "") for candidate in top_candidates]
    system_prompt = render_prompt("online_recommendation.close_reading.system")
    user_prompt = render_prompt(
        "online_recommendation.close_reading.user",
        user_requirement_text=user_requirement_text,
        display_candidates_json=json.dumps(
            display_candidates,
            ensure_ascii=False,
            indent=2,
        ),
        expected_count=len(expected_names),
        expected_names_json=json.dumps(expected_names, ensure_ascii=False),
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


CLOSE_READING_TEXT_FIELDS = (
    "recommendation_reason",
    "matched_needs",
    "strengths",
    "limitations",
    "simple_model_explanation",
)


def _close_reading_item_is_complete(item, allowed_names):
    name = item.get("instance_name")
    if name not in allowed_names:
        return False
    try:
        float(item.get("final_score"))
    except (TypeError, ValueError):
        return False
    return all(str(item.get(field, "")).strip() for field in CLOSE_READING_TEXT_FIELDS)


def _complete_close_reading_items(raw_output, candidate_names):
    allowed_names = set(candidate_names)
    items_by_name = {}
    for item in raw_output.get("ranked_candidates", []) or []:
        name = item.get("instance_name")
        if name in items_by_name:
            continue
        if _close_reading_item_is_complete(item, allowed_names):
            items_by_name[name] = item
    return items_by_name


def _call_close_reading_api(messages, schema, call_name):
    if USE_OPENAI_HARD_SCHEMA:
        if openai_client is None:
            raise RuntimeError("缺少 OPENAI_API_KEY / Missing OPENAI_API_KEY.")
        check_llm_input_budget(messages, model_name=OPENAI_MODEL_NAME, call_name=call_name)
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            temperature=LLM_API_TEMPERATURE,
            messages=messages,
            response_format=openai_json_schema_response_format("opf_direct_recommendation_close_reading", schema),
            timeout=180,
        )
        return json.loads(response.choices[0].message.content)

    if rwth_client is None:
        raise RuntimeError("缺少 RWTH_API_KEY / Missing RWTH_API_KEY.")
    soft_messages = messages + [
        {
            "role": "user",
            "content": render_prompt(
                "common.soft_schema_instruction",
                schema_json=json.dumps(schema, ensure_ascii=False, indent=2),
            ),
        }
    ]
    check_llm_input_budget(soft_messages, model_name=RWTH_MODEL_NAME, call_name=f"{call_name}_rwth")
    response = rwth_client.chat.completions.create(
        model=RWTH_MODEL_NAME,
        temperature=LLM_API_TEMPERATURE,
        messages=soft_messages,
        timeout=180,
    )
    return parse_json_object_from_text(response.choices[0].message.content)


def call_llm_close_reading(user_requirement_text, top_candidates):
    """Close-read every prefilter candidate and repair any incomplete LLM response."""
    if not top_candidates:
        return {"ranked_candidates": [], "overall_summary": "No candidates to review."}

    names = [candidate["kg_info"]["instance_name"] for candidate in top_candidates]
    schema = build_close_reading_schema(names)
    messages = build_close_reading_messages(user_requirement_text, top_candidates)
    best_raw = {"ranked_candidates": [], "overall_summary": ""}
    best_items = {}

    for attempt in range(1, ONLINE_CLOSE_READING_MAX_FULL_ATTEMPTS + 1):
        raw = _call_close_reading_api(
            messages,
            schema,
            call_name=f"online_close_reading_full_attempt_{attempt}",
        )
        items = _complete_close_reading_items(raw, names)
        if len(items) > len(best_items):
            best_raw = raw
            best_items = items
        missing = [name for name in names if name not in items]
        if not missing:
            return raw
        print(
            f"精读返回不完整，第 {attempt} 次缺少 {len(missing)} 个候选，将自动重试。"
            f" / Close-reading attempt {attempt} omitted {len(missing)} candidates; retrying automatically."
        )

    missing = [name for name in names if name not in best_items]
    if missing:
        candidate_by_name = {
            candidate["kg_info"]["instance_name"]: candidate
            for candidate in top_candidates
        }
        repair_candidates = [candidate_by_name[name] for name in missing]
        repair_schema = build_close_reading_schema(missing)
        repair_messages = build_close_reading_messages(user_requirement_text, repair_candidates)
        repair_raw = _call_close_reading_api(
            repair_messages,
            repair_schema,
            call_name="online_close_reading_missing_candidate_repair",
        )
        best_items.update(_complete_close_reading_items(repair_raw, missing))

    still_missing = [name for name in names if name not in best_items]
    if still_missing:
        raise RuntimeError(
            "LLM 精读在自动重试后仍未完整返回所有候选，因此未生成可能失真的 Top-3。"
            " / The LLM still omitted candidates after automatic repair, so no potentially incomplete Top-3 was produced."
            f"\nMissing candidates: {still_missing}"
        )

    return {
        "ranked_candidates": [best_items[name] for name in names],
        "overall_summary": best_raw.get("overall_summary", ""),
    }


def validate_close_reading_output(raw_output, top_candidates):
    """Validate that every candidate has a real, complete close-reading result."""
    allowed = [candidate["kg_info"]["instance_name"] for candidate in top_candidates]
    items_by_name = _complete_close_reading_items(raw_output, allowed)
    missing = [name for name in allowed if name not in items_by_name]
    if missing:
        raise RuntimeError(
            "精读结果不完整，不能安全生成 Top-3。"
            " / Close-reading output is incomplete; a reliable Top-3 cannot be generated."
            f"\nMissing or incomplete candidates: {missing}"
        )

    rows = []
    for name in allowed:
        item = items_by_name[name]
        score = max(0.0, min(100.0, float(item["final_score"])))
        rows.append(
            {
                "rank": int(item.get("rank", len(rows) + 1)),
                "instance_name": name,
                "final_score": score,
                "recommendation_reason": str(item["recommendation_reason"]).strip(),
                "matched_needs": str(item["matched_needs"]).strip(),
                "strengths": str(item["strengths"]).strip(),
                "limitations": str(item["limitations"]).strip(),
                "simple_model_explanation": str(item["simple_model_explanation"]).strip(),
                "close_reading_completed": True,
            }
        )
    rows.sort(key=lambda x: (-x["final_score"], x["rank"]))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return {"ranked_candidates": rows, "overall_summary": raw_output.get("overall_summary", "")}


def print_close_reading_result(close_reading_result, prefilter_result=None, final_top_n=ONLINE_FINAL_TOP_N):
    prefilter_by_name = {
        item["instance_name"]: item
        for item in (prefilter_result or {}).get("selected_candidates", [])
    }

    print("\nLLM 精读分析完整中间结果 / Full LLM close-reading output")
    print("=" * 90)
    print(close_reading_result.get("overall_summary", ""))

    for row in close_reading_result.get("ranked_candidates", []):
        evidence = prefilter_by_name.get(row["instance_name"], {})
        print("\n" + "-" * 90)
        print(f"Rank {row['rank']} | {row['instance_name']}")
        print("最终分 / final_score:", row["final_score"])
        print("初筛分 / prefilter_score:", evidence.get("prefilter_score", ""))
        print("初筛匹配原因 / why_matched:", evidence.get("why_matched", ""))
        print("初筛主要风险 / main_risk_or_gap:", evidence.get("main_risk_or_gap", ""))
        print("推荐理由 / recommendation_reason:", row["recommendation_reason"])
        print("匹配需求 / matched_needs:", row["matched_needs"])
        print("优点 / strengths:", row["strengths"])
        print("不足 / limitations:", row["limitations"])
        print("模型简要解释 / simple_model_explanation:", row["simple_model_explanation"])

    final_top = close_reading_result.get("ranked_candidates", [])[:final_top_n]

    print("\n最终推荐 Top-3 / Final recommended Top-3")
    print("=" * 90)
    if not final_top:
        print("没有候选模型可推荐 / No candidate is available for recommendation.")
    for row in final_top:
        evidence = prefilter_by_name.get(row["instance_name"], {})
        print("\n" + "=" * 90)
        print(f"Top {row['rank']}: {row['instance_name']}")
        print("综合匹配分 / final_score:", row["final_score"])
        print("初筛分 / prefilter_score:", evidence.get("prefilter_score", ""))
        print("推荐理由 / recommendation_reason:", row["recommendation_reason"])
        print("匹配原因 / matched_needs:", row["matched_needs"])
        print("优点 / strengths:", row["strengths"])
        print("不足点 / limitations:", row["limitations"])
        print("模型简单讲解 / simple_model_explanation:", row["simple_model_explanation"])

    return final_top


def run_direct_online_recommendation_pipeline(user_requirement_text):
    """Run grouped prefilter, close-read every candidate, and return Top-3."""
    reset_llm_call_diagnostics()
    prefilter_result = run_llm_grouped_prefilter(
        user_requirement_text=user_requirement_text,
        group_size=ONLINE_PREFILTER_GROUP_SIZE,
    )
    if not prefilter_result.get("selected_candidates"):
        return {
            "prefilter_result": prefilter_result,
            "prefilter_candidates": [],
            "raw_close_reading": None,
            "close_reading_result": {"ranked_candidates": [], "overall_summary": "No candidates passed prefilter."},
            "final_top3": [],
            "llm_input_diagnostics": get_llm_call_diagnostics(),
        }

    prefilter_candidates = build_close_reading_candidates_from_prefilter(prefilter_result)
    print("\n进入精读的全部初筛候选 / All prefilter candidates entering close reading:")
    for idx, candidate in enumerate(prefilter_candidates, start=1):
        evidence = candidate["evidence_package"]
        print(f"{idx}. {candidate['kg_info']['instance_name']} | prefilter_score={evidence.get('prefilter_score')}")

    raw_close_reading = call_llm_close_reading(user_requirement_text, prefilter_candidates)
    close_reading_result = validate_close_reading_output(raw_close_reading, prefilter_candidates)
    final_top3 = close_reading_result.get("ranked_candidates", [])[:ONLINE_FINAL_TOP_N]
    expected_top_count = min(ONLINE_FINAL_TOP_N, len(prefilter_candidates))
    if len(final_top3) != expected_top_count:
        raise RuntimeError(
            f"Top-3 数量校验失败：期望 {expected_top_count}，实际 {len(final_top3)}。"
            f" / Top-3 count validation failed: expected {expected_top_count}, got {len(final_top3)}."
        )

    return {
        "prefilter_result": prefilter_result,
        "prefilter_candidates": prefilter_candidates,
        "raw_close_reading": raw_close_reading,
        "close_reading_result": close_reading_result,
        "final_top3": final_top3,
        "pipeline_stages": [
            "grouped_prefilter",
            "merge_prefilter_candidates",
            "close_read_all_candidates",
            "select_top3",
        ],
        "llm_input_diagnostics": get_llm_call_diagnostics(),
    }


