"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *
from .pdf_processing import *
from .ontology_whitelist import *
from .prompt_loader import render_prompt

# ============================================================
# Two-pass LLM structured extraction with schema constraints.
# ============================================================
#
# Pass 1 extracts only text-valued OPFModel data properties.
# Pass 2 selects only object-property class links: level-2 objective/constraint/parameter classes,
# mathematical problem types, modeled OEO energy technologies, and OEO covered demand sectors.

# Section 8 reuses the unified LLM/API configuration defined in Section 1.1.

import json
import re

PAPER_MODEL_DATA_PROPERTY_NAMES = [
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
    "hasSolutionDetailsSummary",
    "hasModelValidationSummary",
    "hasFindingsSummary",
    "hasStrengthsAndLimitationsSummary",
    "isScenarioSuitability",
    "hasFurtherProperty",
]

PAPER_METADATA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "hasModelName": {"type": "string"},
        "hasPaperTitle": {"type": "string"},
        "hasPublicationYear": {"type": ["integer", "null"]},
        "hasDOI": {"type": ["string", "null"]},
        "hasAuthor": {"type": ["string", "null"]},
        "hasInstitution": {"type": ["string", "null"]},
        "hasPrimaryPurpose": {"type": ["string", "null"]},
        "hasMotivation": {"type": ["string", "null"]},
        "hasSolvedProblem": {"type": ["string", "null"]},
        "hasResearchQuestion": {"type": ["string", "null"]},
        "hasPrimaryOutput": {"type": ["string", "null"]},
        "hasModelFeature": {"type": ["string", "null"]},
        "hasPowerFlowFormulationFeature": {"type": ["string", "null"]},
        "hasTimeHorizonFeature": {"type": ["string", "null"]},
        "hasTemporalResolution": {"type": ["string", "null"]},
        "hasOptimizationHorizon": {"type": ["string", "null"]},
        "hasUncertaintyHandlingFeature": {"type": ["string", "null"]},
        "hasPowerSystemDomainFeature": {"type": ["string", "null"]},
        "hasSolutionMethodEnhancementFeature": {"type": ["string", "null"]},
        "hasModelPerformanceFeature": {"type": ["string", "null"]},
        "hasDemandSideFeature": {"type": ["string", "null"]},
        "hasObjectiveFunction": {"type": ["string", "null"]},
        "hasConstraintFunction": {"type": ["string", "null"]},
        "usesParameter": {"type": ["string", "null"]},
        "hasSolutionDetailsSummary": {"type": ["string", "null"]},
        "hasModelValidationSummary": {"type": ["string", "null"]},
        "hasFindingsSummary": {"type": ["string", "null"]},
        "hasStrengthsAndLimitationsSummary": {"type": ["string", "null"]},
        "isScenarioSuitability": {"type": ["boolean", "null"]},
        "hasFurtherProperty": {"type": ["string", "null"]},
    },
    "required": PAPER_MODEL_DATA_PROPERTY_NAMES,
}

# Before writing paper-model instances, derive names from title keywords without requiring an OPF suffix or limiting them to five words.
MODEL_NAME_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "of", "to", "with", "using", "based",
    "model", "method", "approach", "framework", "paper", "study", "towards", "toward",
}

def normalize_opf_model_name(value, fallback="TitleKeywordsModel"):
    """Clean a title-keyword model name without forcing OPF or a fixed word count."""
    raw = str(value or "").strip()
    if not raw:
        raw = fallback
    tokens = re.findall(r"[A-Za-z0-9]+", raw)
    compact = []
    for token in tokens:
        if token.lower() in MODEL_NAME_STOPWORDS:
            continue
        compact.append(token.upper() if token.isupper() else token)
    if not compact:
        compact = tokens or [fallback]

    seen = set()
    deduped = []
    for token in compact:
        key = token.upper()
        if key not in seen:
            seen.add(key)
            deduped.append(token)
    return " ".join(deduped).strip() or fallback

def apply_model_name_policy_to_metadata(metadata):
    metadata = dict(metadata)
    metadata["hasModelName"] = normalize_opf_model_name(metadata.get("hasModelName"))
    return metadata


CONFIDENCE_THRESHOLD_FOR_ONTOLOGY_WRITE = 0.70

def enum_array_schema(allowed_values):
    # OpenAI structured-output JSON schemas do not allow uniqueItems; deduplicate model responses in Python.
    return {
        "type": "array",
        "items": {"type": "string", "enum": allowed_values},
    }

def confidence_array_schema(allowed_values):
    # Every selected class must carry a confidence score; only scores >= 0.70 are retained.
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "className": {"type": "string", "enum": allowed_values},
                "confidence": {"type": "number"},
            },
            "required": ["className", "confidence"],
        },
    }

def dedupe_preserve_order(values):
    """Remove duplicate LLM selections while preserving order."""
    seen = set()
    result = []
    for value in values or []:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, dict) else value
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result

def dedupe_llm_array_fields(result):
    """Deduplicate every array field in a structured LLM result."""
    for key, value in list(result.items()):
        if isinstance(value, list):
            result[key] = dedupe_preserve_order(value)
    return result

def build_structure_schema():
    properties = {
        "objectiveLevel2": enum_array_schema(OBJECTIVE_LEVEL2_CLASSES),
        "constraintLevel2": enum_array_schema(CONSTRAINT_LEVEL2_CLASSES),
        "parameterLevel2": enum_array_schema(PARAMETER_LEVEL2_CLASSES),
        "objectiveLevel2Confidence": confidence_array_schema(OBJECTIVE_LEVEL2_CLASSES),
        "constraintLevel2Confidence": confidence_array_schema(CONSTRAINT_LEVEL2_CLASSES),
        "parameterLevel2Confidence": confidence_array_schema(PARAMETER_LEVEL2_CLASSES),
    }
    for prop, allowed_classes in FEATURE_ALLOWED_CLASSES_BY_PROPERTY.items():
        properties[prop] = enum_array_schema(allowed_classes)
        properties[prop + "Confidence"] = confidence_array_schema(allowed_classes)
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties.keys()),
    }

def openai_response_format(name, schema):
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": True,
            "schema": schema,
        },
    }

def encode_image_as_data_url(image_path):
    """Convert a local image file into a data URL for OpenAI multimodal chat input."""
    image_path = Path(image_path)
    mime_type = mimetypes.guess_type(str(image_path))[0] or "image/png"
    image_base64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{image_base64}"

def build_multimodal_user_content(user_prompt, image_paths=None):
    """Build text + image content parts for OpenAI chat.completions."""
    content = [{"type": "text", "text": user_prompt}]
    for image_path in image_paths or []:
        path = Path(image_path)
        if not path.exists():
            print(f"警告：图片路径不存在，已跳过 / Warning: image path not found and skipped: {path}")
            continue
        content.append({
            "type": "image_url",
            "image_url": {"url": encode_image_as_data_url(path)},
        })
    return content


def extract_json_from_model_output(text):
    """Parse a JSON object returned by a soft-schema model response."""
    text = str(text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))

def call_json_llm(system_prompt, user_prompt, schema_name, schema, image_paths=None):
    """Call the selected LLM route and return parsed JSON.

    OpenAI hard-schema mode receives both text and images.
    RWTH soft-schema mode remains text-only unless that client is later changed.
    """
    if USE_OPENAI_HARD_SCHEMA:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_multimodal_user_content(user_prompt, image_paths)},
        ]
        if openai_client is None:
            raise RuntimeError("缺少 OPENAI_API_KEY，无法调用 OpenAI 路线 / Missing OPENAI_API_KEY for OpenAI route.")
        check_llm_input_budget(
            messages,
            model_name=OPENAI_MODEL_NAME,
            call_name=f"paper_extraction_{schema_name}",
        )
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            temperature=LLM_API_TEMPERATURE,
            messages=messages,
            response_format=openai_response_format(schema_name, schema),
        )
        return json.loads(response.choices[0].message.content)

    if image_paths:
        print("RWTH 软约束路线在此单元格仅支持文本；图片路径会被忽略 / RWTH soft-schema route is text-only here; image paths are ignored.")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {
            "role": "user",
            "content": render_prompt(
                "common.soft_schema_instruction",
                schema_json=json.dumps(schema, ensure_ascii=False, indent=2),
            ),
        },
    ]
    if rwth_client is None:
        raise RuntimeError("缺少 RWTH_API_KEY，无法调用 RWTH 路线 / Missing RWTH_API_KEY for RWTH route.")
    check_llm_input_budget(
        messages,
        model_name=RWTH_MODEL_NAME,
        call_name=f"paper_extraction_{schema_name}_rwth",
    )
    response = rwth_client.chat.completions.create(
        model=RWTH_MODEL_NAME,
        temperature=LLM_API_TEMPERATURE,
        messages=messages,
    )
    return extract_json_from_model_output(response.choices[0].message.content)

def extract_paper_metadata_with_llm(paper_text, image_paths=None):
    system_prompt = render_prompt("paper_extraction.metadata.system")
    user_prompt = render_prompt(
        "paper_extraction.metadata.user",
        paper_text=paper_text,
    )
    metadata = call_json_llm(system_prompt, user_prompt, "paper_model_metadata", PAPER_METADATA_SCHEMA, image_paths=image_paths)
    return apply_model_name_policy_to_metadata(metadata)

def format_level2_map(selected_level1, level2_by_level1):
    return "\n".join(
        f"{level1}: {level2_by_level1.get(level1, [])}"
        for level1 in selected_level1
    )

def parents_for_level2_class(level2_class, level2_by_level1):
    """Find level-1 parents that contain one selected level-2 class."""
    return [
        level1
        for level1, children in level2_by_level1.items()
        if level2_class in children
    ]

def repair_level2_parent_selection(selected_level1, selected_level2, level2_by_level1, label):
    """Repair a common LLM mistake: selecting level-2 classes but omitting their level-1 parents.

    If a selected level-2 class is valid somewhere in the whitelist, its missing
    level-1 parent is added automatically. If it is not in the whitelist at all,
    it is removed.
    """
    selected_level1 = dedupe_preserve_order(selected_level1)
    repaired_level2 = []
    added_parents = []
    removed_level2 = []

    for class_name in dedupe_preserve_order(selected_level2):
        parents = parents_for_level2_class(class_name, level2_by_level1)
        if not parents:
            removed_level2.append(class_name)
            continue
        for parent in parents:
            if parent not in selected_level1:
                selected_level1.append(parent)
                added_parents.append(parent)
        repaired_level2.append(class_name)

    if added_parents:
        print(f"{label} 自动补全一级父类 / auto-added level-1 parents:", dedupe_preserve_order(added_parents))
    if removed_level2:
        print(f"{label} 删除不在白名单中的二级类 / removed non-whitelist level-2 classes:", removed_level2)

    return dedupe_preserve_order(selected_level1), dedupe_preserve_order(repaired_level2)

def validate_level2_under_selected_level1(selected_level1, selected_level2, level2_by_level1, label):
    allowed_level2 = set(
        class_name
        for level1 in selected_level1
        for class_name in level2_by_level1.get(level1, [])
    )
    invalid = [class_name for class_name in selected_level2 if class_name not in allowed_level2]
    if invalid:
        raise ValueError(
            f"{label} 二级类必须属于已选一级类 / level-2 classes must be under selected level-1 classes. "
            f"Invalid: {invalid}"
        )

def infer_level1_from_selected_level2(selected_level2, level2_by_level1):
    """Infer level-1 parents from selected level-2 classes using the ontology whitelist."""
    inferred = []
    for class_name in selected_level2 or []:
        for level1, children in level2_by_level1.items():
            if class_name in children and level1 not in inferred:
                inferred.append(level1)
    return inferred

def confidence_map_from_entries(entries):
    """Return max confidence per className from LLM confidence entries."""
    confidence_by_class = {}
    for item in entries or []:
        if not isinstance(item, dict):
            continue
        class_name = item.get("className")
        try:
            confidence = float(item.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        if class_name:
            confidence_by_class[class_name] = max(confidence_by_class.get(class_name, 0.0), confidence)
    return confidence_by_class

def filter_selected_classes_by_confidence(result, selection_fields, label):
    """Keep only selections whose LLM confidence is >= threshold."""
    clean_result = {}
    for field in selection_fields:
        confidence_field = field + "Confidence"
        confidence_by_class = confidence_map_from_entries(result.get(confidence_field, []))
        kept = []
        removed = []
        for class_name in dedupe_preserve_order(result.get(field, [])):
            confidence = confidence_by_class.get(class_name, 0.0)
            if confidence >= CONFIDENCE_THRESHOLD_FOR_ONTOLOGY_WRITE:
                kept.append(class_name)
            else:
                removed.append((class_name, confidence))
        clean_result[field] = kept
        if removed:
            print(
                f"{label} 低置信度类已移除 / low-confidence classes removed from {field}:",
                removed,
                f"阈值 / threshold={CONFIDENCE_THRESHOLD_FOR_ONTOLOGY_WRITE}",
            )
    return clean_result

def extract_model_structure_with_llm(paper_text, image_paths=None):
    schema = build_structure_schema()
    system_prompt = render_prompt("paper_extraction.structure.system")
    object_feature_text = format_object_feature_whitelist(
        ONTOLOGY_CLASS_LABELS,
        FEATURE_ALLOWED_CLASSES_BY_PROPERTY,
    )
    user_prompt = render_prompt(
        "paper_extraction.structure.user",
        objective_level2_map=format_level2_map(
            OBJECTIVE_LEVEL1_CLASSES,
            OBJECTIVE_LEVEL2_BY_LEVEL1,
        ),
        constraint_level2_map=format_level2_map(
            CONSTRAINT_LEVEL1_CLASSES,
            CONSTRAINT_LEVEL2_BY_LEVEL1,
        ),
        parameter_level2_map=format_level2_map(
            PARAMETER_LEVEL1_CLASSES,
            PARAMETER_LEVEL2_BY_LEVEL1,
        ),
        object_feature_text=object_feature_text,
        paper_text=paper_text,
    )
    result = call_json_llm(system_prompt, user_prompt, "paper_model_object_property_mapping", schema, image_paths=image_paths)
    result = dedupe_llm_array_fields(result)
    result = filter_selected_classes_by_confidence(
        result,
        [
            "objectiveLevel2",
            "constraintLevel2",
            "parameterLevel2",
            *FEATURE_ALLOWED_CLASSES_BY_PROPERTY.keys(),
        ],
        "Object-property mapping / 对象属性映射",
    )

    result["objectiveLevel1"] = infer_level1_from_selected_level2(result["objectiveLevel2"], OBJECTIVE_LEVEL2_BY_LEVEL1)
    result["constraintLevel1"] = infer_level1_from_selected_level2(result["constraintLevel2"], CONSTRAINT_LEVEL2_BY_LEVEL1)
    result["parameterLevel1"] = infer_level1_from_selected_level2(result["parameterLevel2"], PARAMETER_LEVEL2_BY_LEVEL1)

    validate_level2_under_selected_level1(
        result["objectiveLevel1"],
        result["objectiveLevel2"],
        OBJECTIVE_LEVEL2_BY_LEVEL1,
        "Objective / 目标函数",
    )
    validate_level2_under_selected_level1(
        result["constraintLevel1"],
        result["constraintLevel2"],
        CONSTRAINT_LEVEL2_BY_LEVEL1,
        "Constraint / 约束函数",
    )
    validate_level2_under_selected_level1(
        result["parameterLevel1"],
        result["parameterLevel2"],
        PARAMETER_LEVEL2_BY_LEVEL1,
        "Parameter / 参数变量",
    )
    return result

def save_paper_model_record(record, output_dir=None):
    """Save the two-pass LLM output before ontology writing."""
    output_dir = Path(output_dir or PAPER_PROCESSING_OUTPUT_DIR / record["paper_record"]["paper_name"])
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path = output_dir / "paper_model_record.json"
    portable_record = make_project_paths_portable(record)
    record_path.write_text(
        json.dumps(portable_record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return record_path

def load_paper_model_record(record_path):
    """Load a previously saved two-pass LLM output."""
    record_path = Path(record_path)
    return json.loads(record_path.read_text(encoding="utf-8"))

def make_source_id(paper_path):
    """Create a stable source id from one paper path.

    This function belongs in the extraction cell because paper_model_record is
    created before the ontology-writing helper cell is run.
    """
    paper_path = Path(paper_path)
    source_id = re.sub(r"[^A-Za-z0-9_]+", "_", paper_path.stem)
    source_id = re.sub(r"_+", "_", source_id).strip("_")
    return source_id or "paper_model_source"

def extract_paper_model_record(paper_path, paper_record_output_dir=None, save_intermediate=True):
    """Run the two LLM passes for one paper and merge the result.

    The returned paper_model_record is the main intermediate object:
      - metadata: pass 1 data-property extraction
      - structure: pass 2 objective / constraint / parameter object-property classes
      - features: pass 2 remaining feature object-property classes

    Most model features are now data-property text fields from pass 1.
    Only hasMathematicalProblemType, hasModeledTechnology, and OEO coversSector remain feature-like object links; all other model features stay as data-property text.
    """
    paper_record = extract_paper_record(paper_path, output_dir=paper_record_output_dir)
    paper_text = paper_record["llm_payload"]["prompt_text"]
    image_paths = paper_record["llm_payload"]["image_input_paths"]
    metadata = extract_paper_metadata_with_llm(paper_text, image_paths=image_paths)
    object_mapping = extract_model_structure_with_llm(paper_text, image_paths=image_paths)
    features = {
        prop: object_mapping.pop(prop, [])
        for prop in FEATURE_ALLOWED_CLASSES_BY_PROPERTY
    }
    record = {
        "source_id": make_source_id(paper_path),
        "paper_path": str(paper_path),
        "paper_record": paper_record,
        "metadata": metadata,
        "structure": object_mapping,
        "features": features,
        "llm_outputs": {
            "pass_1_data_properties": metadata,
            "pass_2_object_properties": {
                "structure": object_mapping,
                "features": features,
            },
        },
    }
    if save_intermediate:
        record["paper_model_record_path"] = str(save_paper_model_record(record, output_dir=paper_record_output_dir))
    return record


def build_review_removal_schema():
    """Build a schema for the final high-confidence LLM review gate."""
    metadata_fields = [
        key for key in PAPER_METADATA_SCHEMA["properties"].keys()
        if key != "hasModelName"
    ]
    feature_removal_properties = {
        prop: enum_array_schema(allowed_classes)
        for prop, allowed_classes in FEATURE_ALLOWED_CLASSES_BY_PROPERTY.items()
    }
    structure_removal_properties = {
        "objectiveLevel1": enum_array_schema(OBJECTIVE_LEVEL1_CLASSES),
        "objectiveLevel2": enum_array_schema(OBJECTIVE_LEVEL2_CLASSES),
        "constraintLevel1": enum_array_schema(CONSTRAINT_LEVEL1_CLASSES),
        "constraintLevel2": enum_array_schema(CONSTRAINT_LEVEL2_CLASSES),
        "parameterLevel1": enum_array_schema(PARAMETER_LEVEL1_CLASSES),
        "parameterLevel2": enum_array_schema(PARAMETER_LEVEL2_CLASSES),
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "hasHighConfidenceErrors": {"type": "boolean"},
            "dataPropertiesToSetNone": enum_array_schema(metadata_fields),
            "structureRelationsToRemove": {
                "type": "object",
                "additionalProperties": False,
                "properties": structure_removal_properties,
                "required": list(structure_removal_properties.keys()),
            },
            "featureRelationsToRemove": {
                "type": "object",
                "additionalProperties": False,
                "properties": feature_removal_properties,
                "required": list(feature_removal_properties.keys()),
            },
            "reviewSummaryZh": {"type": "string"},
            "reviewSummaryEn": {"type": "string"},
        },
        "required": [
            "hasHighConfidenceErrors",
            "dataPropertiesToSetNone",
            "structureRelationsToRemove",
            "featureRelationsToRemove",
            "reviewSummaryZh",
            "reviewSummaryEn",
        ],
    }

def apply_review_pruning(record, review):
    """Apply the review result by only deleting or setting fields to None."""
    record = copy.deepcopy(record)

    for property_name in review.get("dataPropertiesToSetNone", []):
        if property_name in record.get("metadata", {}) and property_name != "hasModelName":
            record["metadata"][property_name] = None

    structure = record.get("structure", {})
    for key, values_to_remove in review.get("structureRelationsToRemove", {}).items():
        remove_set = set(values_to_remove or [])
        structure[key] = [
            value for value in structure.get(key, [])
            if value not in remove_set
        ]

    features = record.get("features", {})
    for key, values_to_remove in review.get("featureRelationsToRemove", {}).items():
        remove_set = set(values_to_remove or [])
        features[key] = [
            value for value in features.get(key, [])
            if value not in remove_set
        ]

    record["llm_review"] = review
    record["llm_review_applied"] = True
    record["llm_outputs"] = {
        "pass_1_metadata": record["metadata"],
        "pass_2_structure": record["structure"],
        "pass_2_feature_object_properties": record["features"],
        "pass_4_high_confidence_review": review,
    }
    return record

def review_and_prune_paper_model_record(record):
    """Ask the LLM to remove only obvious high-confidence extraction errors.

    Rule: the review pass may not add new classes, replace classes, rename
    classes, or edit text. It can only mark existing data properties as None
    or remove existing object-property selections when the error is obvious
    with at least 80% confidence.
    """
    schema = build_review_removal_schema()
    paper_record = record["paper_record"]
    paper_text = paper_record["llm_payload"]["prompt_text"]
    image_paths = paper_record["llm_payload"]["image_input_paths"]

    current_result = {
        "metadata": record.get("metadata", {}),
        "structure": record.get("structure", {}),
        "features": record.get("features", {}),
    }
    system_prompt = render_prompt("paper_extraction.review.system")
    user_prompt = render_prompt(
        "paper_extraction.review.user",
        current_result_json=json.dumps(current_result, ensure_ascii=False, indent=2),
        paper_text=paper_text,
    )
    review = call_json_llm(
        system_prompt,
        user_prompt,
        "paper_model_high_confidence_review",
        schema,
        image_paths=image_paths,
    )
    review = dedupe_llm_array_fields(review)
    review["structureRelationsToRemove"] = dedupe_llm_array_fields(review.get("structureRelationsToRemove", {}))
    review["featureRelationsToRemove"] = dedupe_llm_array_fields(review.get("featureRelationsToRemove", {}))
    pruned_record = apply_review_pruning(record, review)

    if record.get("paper_model_record_path"):
        review_path = Path(record["paper_model_record_path"]).with_name("paper_model_record_reviewed.json")
        portable_record = make_project_paths_portable(pruned_record)
        review_path.write_text(
            json.dumps(portable_record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        pruned_record["reviewed_paper_model_record_path"] = str(review_path)

    return pruned_record

def print_review_summary(record):
    """Print the high-confidence review summary in a readable way."""
    review = record.get("llm_review")
    if not review:
        print("尚未执行第 4 轮复核 / Review pass has not been run yet.")
        return
    print("\n第 4 轮 LLM 高置信度复核结果 / Pass-4 high-confidence review")
    print("是否发现高置信度明显错误 / Has high-confidence errors:", review.get("hasHighConfidenceErrors"))
    print("中文摘要 / Chinese summary:", review.get("reviewSummaryZh"))
    print("English summary:", review.get("reviewSummaryEn"))
    print("置空的数据属性 / Data properties set to None:", review.get("dataPropertiesToSetNone"))
    print("删除的结构关系 / Removed structure relations:")
    print(json.dumps(review.get("structureRelationsToRemove", {}), ensure_ascii=False, indent=2))
    print("删除的模型特征关系 / Removed feature relations:")
    print(json.dumps(review.get("featureRelationsToRemove", {}), ensure_ascii=False, indent=2))

