"""Gold-standard evaluation for LLM-ingested PaperModel data properties."""

from __future__ import annotations

import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from .config import *
from .paper_extraction import call_json_llm
from .prompt_loader import prompt_fingerprint, render_prompt


# Human Gold records are translated to English before semantic comparison.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")

SEMANTIC_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
SEMANTIC_MODEL_CACHE_DIR = SENTENCE_TRANSFORMERS_CACHE_DIR

# hasModelName remains excluded because model-name wording is not graded.
# isScenarioSuitability is Boolean and is not meaningful for sentence embeddings.
# The remaining 28 data properties are evaluated for every matched paper.
SEMANTIC_DATA_PROPERTY_FIELDS = [
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
    "hasFurtherProperty",
]

FIELD_LABELS = {
    "hasPaperTitle": ("Paper title", "论文标题"),
    "hasPublicationYear": ("Publication year", "出版年份"),
    "hasDOI": ("DOI", "DOI"),
    "hasAuthor": ("Authors", "作者"),
    "hasInstitution": ("Institutions", "机构"),
    "hasPrimaryPurpose": ("Primary purpose", "主要目的"),
    "hasMotivation": ("Research motivation", "研究动机"),
    "hasSolvedProblem": ("Solved problem", "已解决问题"),
    "hasResearchQuestion": ("Research question", "研究问题"),
    "hasPrimaryOutput": ("Primary output", "主要输出"),
    "hasModelFeature": ("Model features", "模型特征"),
    "hasPowerFlowFormulationFeature": ("Power-flow formulation", "潮流模型特征"),
    "hasTimeHorizonFeature": ("Time-horizon feature", "时间范围特征"),
    "hasTemporalResolution": ("Temporal resolution", "时间分辨率"),
    "hasOptimizationHorizon": ("Optimization horizon", "优化时域"),
    "hasUncertaintyHandlingFeature": ("Uncertainty handling", "不确定性处理"),
    "hasPowerSystemDomainFeature": ("Power-system domain", "电力系统领域"),
    "hasSolutionMethodEnhancementFeature": ("Solution-method enhancement", "求解方法增强"),
    "hasModelPerformanceFeature": ("Model performance", "模型性能特征"),
    "hasDemandSideFeature": ("Demand-side feature", "需求侧特征"),
    "hasObjectiveFunction": ("Objective function", "目标函数"),
    "hasConstraintFunction": ("Constraint function", "约束函数"),
    "usesParameter": ("Parameters", "使用参数"),
    "hasSolutionDetailsSummary": ("Solution details", "求解细节概要"),
    "hasModelValidationSummary": ("Model validation", "模型验证概要"),
    "hasFindingsSummary": ("Research findings", "研究发现概要"),
    "hasStrengthsAndLimitationsSummary": ("Strengths and limitations", "优势与局限概要"),
    "hasFurtherProperty": ("Other properties", "其他属性"),
}

EXACT_MATCH_FIELDS = {
    "hasPaperTitle",
    "hasPublicationYear",
    "hasDOI",
}

SEMANTIC_HUMAN_INFO_DIR = HUMAN_PAPER_MODEL_RECORD_DIR
SEMANTIC_HUMAN_PAPER_RECORD_DIR = HUMAN_PAPER_MODEL_RECORD_DIR
PAPER_INGESTION_QUALITY_VALIDATION_DIR = (
    PAPER_INGESTION_VALIDATION_RESULTS_DIR
)
PAPER_INGESTION_SEMANTIC_SIMILARITY_DETAILS_CSV = (
    PAPER_INGESTION_VALIDATION_REPORTS_DIR
    / "01_field_semantic_similarity_details.csv"
)
PAPER_INGESTION_FACTUAL_ACCURACY_DETAILS_CSV = (
    PAPER_INGESTION_VALIDATION_REPORTS_DIR
    / "02_field_factual_accuracy_details.csv"
)
PAPER_INGESTION_VALIDATION_SUMMARY_CSV = (
    PAPER_INGESTION_VALIDATION_REPORTS_DIR
    / "03_overall_summary.csv"
)
HUMAN_GOLD_ENGLISH_TRANSLATION_CACHE_JSON = (
    PAPER_INGESTION_VALIDATION_CACHE_DIR
    / "01_human_gold_english_translations.json"
)
HUMAN_GOLD_TRANSLATION_CACHE_VERSION = 1
FIELD_FACTUAL_JUDGMENT_CACHE_JSON = (
    PAPER_INGESTION_VALIDATION_CACHE_DIR
    / "02_field_factual_judgments.json"
)
FIELD_FACTUAL_JUDGMENT_CACHE_VERSION = 1
HUMAN_GOLD_TRANSLATION_PROMPT_IDS = (
    "semantic_evaluation.gold_translation.system",
    "semantic_evaluation.gold_translation.user",
    "common.soft_schema_instruction",
)
FIELD_FACTUAL_JUDGMENT_PROMPT_IDS = (
    "semantic_evaluation.factual_judgment.system",
    "semantic_evaluation.factual_judgment.user",
    "common.soft_schema_instruction",
)


def current_human_gold_translation_prompt_hash() -> str:
    """Hash the prompt text currently on disk so edits invalidate old translations."""
    return prompt_fingerprint(*HUMAN_GOLD_TRANSLATION_PROMPT_IDS)


def current_field_factual_judgment_prompt_hash() -> str:
    """Hash the prompt text currently on disk so edits invalidate old judgments."""
    return prompt_fingerprint(*FIELD_FACTUAL_JUDGMENT_PROMPT_IDS)

SEMANTIC_RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
SEMANTIC_RDF_ABOUT = f"{{{SEMANTIC_RDF_NS}}}about"
SEMANTIC_RDF_RESOURCE = f"{{{SEMANTIC_RDF_NS}}}resource"

MISSING_VALUE_MARKERS = {
    "",
    "none",
    "null",
    "n/a",
    "na",
    "unknown",
    "not available",
    "not provided",
    "not specified",
    "not applicable",
    "not reported",
    "none reported",
    "未明确",
    "未提供",
    "未给出",
    "不适用",
    "未知",
}
MISSING_VALUE_PHRASES = (
    "上传 pdf 中未明确",
    "论文未明确",
    "论文中未明确",
    "未明确给出",
    "未明确标注",
    "未提供",
    "未给出",
    "不适用",
    "not available",
    "not provided",
    "not specified",
    "not applicable",
    "not reported",
    "none reported",
)


def resolve_local_sentence_transformer_snapshot(model_name=SEMANTIC_MODEL_NAME):
    """Return the newest complete local snapshot for a sentence-transformer."""
    repo_directory_name = "models--" + str(model_name).replace("/", "--")
    candidate_cache_roots = [
        SEMANTIC_MODEL_CACHE_DIR,
        Path(
            os.environ.get(
                "HF_HOME",
                Path.home() / ".cache" / "huggingface",
            )
        ) / "hub",
    ]
    snapshots = []
    for cache_root in candidate_cache_roots:
        snapshots_dir = cache_root / repo_directory_name / "snapshots"
        if snapshots_dir.exists():
            snapshots.extend(
                path
                for path in snapshots_dir.iterdir()
                if path.is_dir()
            )
    snapshots.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    required_files = ("modules.json", "config.json", "tokenizer_config.json")
    model_weight_files = ("model.safetensors", "pytorch_model.bin")
    for snapshot in snapshots:
        if (
            all((snapshot / filename).exists() for filename in required_files)
            and any(
                (snapshot / filename).exists()
                for filename in model_weight_files
            )
        ):
            return snapshot
    return None


def load_sentence_transformer_model(model_name=SEMANTIC_MODEL_NAME):
    """Load the multilingual sentence-transformer from the project cache."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "缺少 sentence-transformers，请在当前虚拟环境安装："
            " pip install -U sentence-transformers / "
            "Missing sentence-transformers package."
        ) from exc

    SEMANTIC_MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    local_snapshot = resolve_local_sentence_transformer_snapshot(model_name)
    if local_snapshot is not None:
        print("使用本地 embedding 模型 / Using local embedding model:", local_snapshot)
        return SentenceTransformer(
            str(local_snapshot),
            cache_folder=str(SEMANTIC_MODEL_CACHE_DIR),
        )

    print("下载并加载多语言模型 / Downloading multilingual model:", model_name)
    return SentenceTransformer(
        model_name,
        cache_folder=str(SEMANTIC_MODEL_CACHE_DIR),
    )


def clean_field_text(value) -> str:
    """Normalize markdown noise while preserving the field meaning."""
    text = str(value or "").replace("\r", "\n")
    text = re.sub(r"^\s*---+\s*$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_missing_field_value(value) -> bool:
    normalized = re.sub(r"\s+", " ", clean_field_text(value)).strip().lower()
    normalized_without_terminal_punctuation = normalized.rstrip(" .;:!?")
    if normalized in MISSING_VALUE_MARKERS:
        return True
    if normalized_without_terminal_punctuation in MISSING_VALUE_MARKERS:
        return True
    return any(
        normalized.startswith(phrase)
        for phrase in MISSING_VALUE_PHRASES
    )


def semantic_normalize_identity_text(value) -> str:
    """Normalize DOI, title, year, and other identity strings."""
    raw_value = clean_field_text(value).lower()
    if is_missing_field_value(raw_value):
        return ""
    missing_fragments = (
        "未明确",
        "未提供",
        "未给出",
        "not available",
        "not provided",
        "not specified",
        "unknown",
    )
    if "doi" in raw_value and any(
        fragment in raw_value for fragment in missing_fragments
    ):
        return ""
    raw_value = raw_value.replace("https://doi.org/", "")
    raw_value = raw_value.replace("http://doi.org/", "")
    raw_value = re.sub(r"^doi\s*:\s*", "", raw_value)
    raw_value = re.sub(r"[^a-z0-9]+", " ", raw_value)
    return " ".join(raw_value.split())


def parse_human_markdown_fields_for_similarity(md_text):
    """Parse only the human-curated data-property section.

    The parser stops when the object-property section begins, so repeated
    hasObjectiveFunction/hasConstraintFunction/usesParameter headings in that
    section cannot contaminate the data-property Gold values.
    """
    fields: dict[str, str] = {}
    valid_fields = set(SEMANTIC_DATA_PROPERTY_FIELDS) | {
        "hasModelName",
        "isScenarioSuitability",
    }
    current_field = None
    current_lines: list[str] = []
    started = False

    def normalize_heading(line):
        value = str(line or "").strip()
        value = re.sub(r"^#+\s*", "", value).strip()
        if value.startswith("**") and value.endswith("**"):
            value = value[2:-2].strip()
        return value

    def is_section_boundary(heading):
        normalized = re.sub(r"\s+", " ", str(heading or "")).strip()
        normalized_lower = normalized.lower()
        section_names = (
            "papermetadata",
            "motivationandsolvedproblem",
            "modelfeature",
            "modelstructure",
            "solutiondetails",
            "modelvalidation",
            "findings",
            "strengthsandlimitations",
            "additionalinformation",
        )
        if re.fullmatch(
            rf"\d+\.\s*(?:{'|'.join(section_names)})",
            normalized_lower,
        ):
            return True
        return normalized_lower in {
            "dataproperty",
            "dataproperty 数据属性",
            "data property",
            "data property 数据属性",
            "论文与模型基础识别信息",
            "模型提出动机与解决的问题",
            "模型特征标签",
            "模型结构信息",
        }

    def flush():
        nonlocal current_field, current_lines
        if current_field:
            value = clean_field_text("\n".join(current_lines))
            if value:
                fields[current_field] = value
        current_field = None
        current_lines = []

    for line in str(md_text or "").splitlines():
        heading = normalize_heading(line)
        heading_lower = heading.lower()
        if started and (
            "objective property" in heading_lower
            or "object property" in heading_lower
            or "对象属性" in heading
        ):
            flush()
            break
        if is_section_boundary(heading):
            flush()
            continue
        if heading in valid_fields:
            flush()
            started = True
            current_field = heading
        elif current_field:
            current_lines.append(line)
    flush()
    return fields


def semantic_local_name_from_resource(resource):
    if not resource:
        return ""
    value = str(resource)
    if value.startswith("#"):
        return value[1:]
    if value.startswith(OPF_IRI):
        return value[len(OPF_IRI):]
    if "#" in value:
        return value.rsplit("#", 1)[-1]
    return value.rsplit("/", 1)[-1]


def semantic_is_opfmodel_individual(individual):
    return any(
        child.tag.endswith("}type")
        and semantic_local_name_from_resource(
            child.attrib.get(SEMANTIC_RDF_RESOURCE)
        )
        == "OPFModel"
        for child in individual
    )


def read_opfmodel_data_records_for_similarity():
    """Read all LLM-ingested OPFModel data properties from the knowledge graph."""
    owl_path = resolve_instance_owl_read_path()
    root = ET.fromstring(owl_path.read_text(encoding="utf-8"))
    records = []
    for individual in root.iter():
        if not individual.tag.endswith("}NamedIndividual"):
            continue
        if not semantic_is_opfmodel_individual(individual):
            continue
        data: dict[str, list[str]] = {}
        for child in individual:
            tag = child.tag.split("}", 1)[-1]
            if tag == "type" or child.attrib.get(SEMANTIC_RDF_RESOURCE):
                continue
            data.setdefault(tag, []).append(clean_field_text(child.text))
        records.append(
            {
                "iri": individual.attrib.get(SEMANTIC_RDF_ABOUT, ""),
                "local_name": semantic_local_name_from_resource(
                    individual.attrib.get(SEMANTIC_RDF_ABOUT, "")
                ),
                "data_properties": {
                    key: "; ".join(value for value in values if value)
                    for key, values in data.items()
                    if any(values)
                },
            }
        )
    return records


def collect_human_paper_record_markdowns(extra_dirs=None):
    """Collect unique human Gold records from the integrated markdown folder."""
    candidate_dirs = [SEMANTIC_HUMAN_PAPER_RECORD_DIR]
    if extra_dirs:
        candidate_dirs.extend(Path(path) for path in extra_dirs)

    records = []
    seen = set()
    for folder in candidate_dirs:
        folder = Path(folder)
        if not folder.exists():
            continue
        for md_path in sorted(folder.rglob("*.md"), key=lambda path: str(path).lower()):
            fields = parse_human_markdown_fields_for_similarity(
                md_path.read_text(encoding="utf-8", errors="ignore")
            )
            doi_key = semantic_normalize_identity_text(fields.get("hasDOI"))
            title_key = semantic_normalize_identity_text(fields.get("hasPaperTitle"))
            if not doi_key and not title_key:
                continue
            identity_key = ("doi", doi_key) if doi_key else ("title", title_key)
            if identity_key in seen:
                continue
            seen.add(identity_key)
            records.append(
                {
                    "path": md_path,
                    "fields": fields,
                    "doi_key": doi_key,
                    "title_key": title_key,
                }
            )
    return records


def contains_cjk(value) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", str(value or "")))


def human_gold_record_cache_key(record) -> str:
    doi_key = record.get("doi_key", "")
    title_key = record.get("title_key", "")
    if doi_key:
        return f"doi:{doi_key}"
    if title_key:
        return f"title:{title_key}"
    return f"path:{Path(record['path']).name}"


def human_gold_source_hash(fields) -> str:
    payload = {
        field: clean_field_text(fields.get(field, ""))
        for field in sorted(fields)
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def load_human_gold_english_translation_cache():
    current_prompt_hash = current_human_gold_translation_prompt_hash()
    if not HUMAN_GOLD_ENGLISH_TRANSLATION_CACHE_JSON.exists():
        return {
            "version": HUMAN_GOLD_TRANSLATION_CACHE_VERSION,
            "prompt_hash": current_prompt_hash,
            "model": MODEL_NAME,
            "records": {},
        }
    try:
        payload = json.loads(
            HUMAN_GOLD_ENGLISH_TRANSLATION_CACHE_JSON.read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError):
        payload = {}
    if (
        payload.get("version") != HUMAN_GOLD_TRANSLATION_CACHE_VERSION
        or payload.get("prompt_hash") != current_prompt_hash
        or payload.get("model") != MODEL_NAME
    ):
        payload = {}
    payload.setdefault("version", HUMAN_GOLD_TRANSLATION_CACHE_VERSION)
    payload.setdefault("prompt_hash", current_prompt_hash)
    payload.setdefault("model", MODEL_NAME)
    payload.setdefault("records", {})
    return payload


def save_human_gold_english_translation_cache(cache):
    HUMAN_GOLD_ENGLISH_TRANSLATION_CACHE_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    HUMAN_GOLD_ENGLISH_TRANSLATION_CACHE_JSON.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def translate_one_human_gold_record_to_english(record):
    """Faithfully translate Chinese/mixed Gold fields without summarizing them."""
    source_fields = {
        field: clean_field_text(record.get("fields", {}).get(field, ""))
        for field in SEMANTIC_DATA_PROPERTY_FIELDS
    }
    fields_to_translate = {
        field: value
        for field, value in source_fields.items()
        if value
        and not is_missing_field_value(value)
        and contains_cjk(value)
    }
    translated_fields = dict(source_fields)
    if not fields_to_translate:
        return translated_fields

    translation_properties = {
        field: {"type": "string"}
        for field in fields_to_translate
    }
    schema = {
        "type": "object",
        "properties": translation_properties,
        "required": list(translation_properties),
        "additionalProperties": False,
    }
    system_prompt = render_prompt("semantic_evaluation.gold_translation.system")
    user_prompt = render_prompt(
        "semantic_evaluation.gold_translation.user",
        fields_to_translate_json=json.dumps(
            fields_to_translate,
            ensure_ascii=False,
            indent=2,
        ),
    )
    result = call_json_llm(
        system_prompt,
        user_prompt,
        "human_gold_english_translation",
        schema,
        image_paths=None,
    )
    missing_translations = [
        field
        for field in fields_to_translate
        if not clean_field_text(result.get(field, ""))
    ]
    if missing_translations:
        raise RuntimeError(
            "人工Gold英文翻译缺少字段 / Human Gold translation omitted fields: "
            + ", ".join(missing_translations)
        )
    for field in fields_to_translate:
        translated_fields[field] = clean_field_text(result[field])
    return translated_fields


def translate_human_gold_records_to_english(
    human_records,
    force=False,
    progress_callback=None,
):
    """Return English Gold records, reusing a per-paper translation cache."""
    cache = load_human_gold_english_translation_cache()
    translated_records = []
    total = len(human_records)

    for index, record in enumerate(human_records, start=1):
        source_fields = dict(record.get("fields", {}))
        cache_key = human_gold_record_cache_key(record)
        source_hash = human_gold_source_hash(source_fields)
        cached = cache["records"].get(cache_key, {})
        cached_fields = cached.get("english_fields", {})
        cache_valid = (
            not force
            and cached.get("source_hash") == source_hash
            and all(
                field in cached_fields
                for field in SEMANTIC_DATA_PROPERTY_FIELDS
            )
        )

        if cache_valid:
            english_fields = {
                **source_fields,
                **cached_fields,
            }
            cache_state_en = "cached"
            cache_state_zh = "使用缓存"
        else:
            english_fields = {
                **source_fields,
                **translate_one_human_gold_record_to_english(record),
            }
            cache["records"][cache_key] = {
                "source_hash": source_hash,
                "source_file": project_relative_path(record.get("path", "")),
                "english_fields": {
                    field: english_fields.get(field, "")
                    for field in SEMANTIC_DATA_PROPERTY_FIELDS
                },
            }
            save_human_gold_english_translation_cache(cache)
            cache_state_en = "translated"
            cache_state_zh = "已翻译"

        translated_record = dict(record)
        translated_record["original_fields"] = source_fields
        translated_record["fields"] = english_fields
        translated_records.append(translated_record)

        if progress_callback is not None:
            progress = 12 + int(23 * index / max(total, 1))
            progress_callback(
                progress,
                f"Human Gold English translation {index}/{total} ({cache_state_en})",
                f"人工Gold英文翻译 {index}/{total}（{cache_state_zh}）",
            )

    return translated_records


def load_field_factual_judgment_cache():
    """Load cached per-paper LLM factual judgments."""
    current_prompt_hash = current_field_factual_judgment_prompt_hash()
    if not FIELD_FACTUAL_JUDGMENT_CACHE_JSON.exists():
        return {
            "version": FIELD_FACTUAL_JUDGMENT_CACHE_VERSION,
            "prompt_hash": current_prompt_hash,
            "model": MODEL_NAME,
            "records": {},
        }
    try:
        payload = json.loads(
            FIELD_FACTUAL_JUDGMENT_CACHE_JSON.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        payload = {}
    cache_is_current = (
        payload.get("version") == FIELD_FACTUAL_JUDGMENT_CACHE_VERSION
        and payload.get("prompt_hash") == current_prompt_hash
        and payload.get("model") == MODEL_NAME
    )
    if not cache_is_current:
        payload = {}
    payload.setdefault("version", FIELD_FACTUAL_JUDGMENT_CACHE_VERSION)
    payload.setdefault("prompt_hash", current_prompt_hash)
    payload.setdefault("model", MODEL_NAME)
    payload.setdefault("records", {})
    return payload


def save_field_factual_judgment_cache(cache):
    """Persist factual judgments after every paper so an interrupted run can resume."""
    FIELD_FACTUAL_JUDGMENT_CACHE_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    FIELD_FACTUAL_JUDGMENT_CACHE_JSON.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _field_judgment_cache_key(paper_pairs):
    first = paper_pairs[0]
    instance_name = str(first.get("Matched instance / 匹配实例", "")).strip()
    paper_title = semantic_normalize_identity_text(
        first.get("Paper title / 论文标题", "")
    )
    return instance_name or paper_title


def _field_judgment_source_hash(comparable_pairs):
    payload = {
        pair["Field / 字段"]: {
            "gold": clean_field_text(pair.get("_human_value", "")),
            "llm": clean_field_text(pair.get("_llm_value", "")),
        }
        for pair in comparable_pairs
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def judge_paper_fields_with_llm(comparable_pairs):
    """Judge factual correctness for one paper without using similarity thresholds."""
    field_payload = {
        pair["Field / 字段"]: {
            "human_gold_standard": pair["_human_value"],
            "llm_extracted_value": pair["_llm_value"],
        }
        for pair in comparable_pairs
    }
    judgment_schema = {
        "type": "object",
        "properties": {
            field: {
                "type": "object",
                "properties": {
                    "factually_correct": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["factually_correct", "reason"],
                "additionalProperties": False,
            }
            for field in field_payload
        },
        "required": list(field_payload),
        "additionalProperties": False,
    }
    system_prompt = render_prompt("semantic_evaluation.factual_judgment.system")
    user_prompt = render_prompt(
        "semantic_evaluation.factual_judgment.user",
        field_payload_json=json.dumps(
            field_payload,
            ensure_ascii=False,
            indent=2,
        ),
    )
    return call_json_llm(
        system_prompt,
        user_prompt,
        "paper_model_field_factual_accuracy",
        judgment_schema,
        image_paths=None,
    )


def find_human_record_for_opf_record(opf_record, human_records):
    """Match one LLM-ingested KG record to its human Gold record."""
    data = opf_record.get("data_properties", {})
    doi_key = semantic_normalize_identity_text(data.get("hasDOI"))
    title_key = semantic_normalize_identity_text(data.get("hasPaperTitle"))
    if doi_key:
        for human_record in human_records:
            if human_record["doi_key"] and human_record["doi_key"] == doi_key:
                return human_record, "DOI exact match / DOI精确匹配"
    if title_key:
        for human_record in human_records:
            if human_record["title_key"] and human_record["title_key"] == title_key:
                return human_record, "title exact match / 标题精确匹配"
    return None, "no Gold match / 未匹配到人工Gold"


def cosine_similarity_matrix(a, b):
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    a = a / np.clip(np.linalg.norm(a, axis=1, keepdims=True), 1e-12, None)
    b = b / np.clip(np.linalg.norm(b, axis=1, keepdims=True), 1e-12, None)
    return a @ b.T


def single_line_text(value):
    """Keep the complete field value while making one CSV row one text line."""
    return re.sub(r"\s+", " ", clean_field_text(value)).strip()


def _build_field_pairs(kg_records, human_records, max_papers=None):
    pairs = []
    issues = []
    matched_papers = []
    extra_kg_records = []
    records = sorted(
        kg_records,
        key=lambda record: semantic_normalize_identity_text(
            record.get("data_properties", {}).get("hasPaperTitle")
            or record.get("local_name")
        ),
    )
    if max_papers is not None:
        records = records[: int(max_papers)]

    matches_by_human_record = {
        id(human_record): []
        for human_record in human_records
    }
    match_by_kg_record = {}
    for opf_record in records:
        human_record, match_reason = find_human_record_for_opf_record(
            opf_record,
            human_records,
        )
        if human_record is None:
            extra_kg_records.append(opf_record)
            continue
        matches_by_human_record[id(human_record)].append(
            (opf_record, match_reason)
        )
        match_by_kg_record[id(opf_record)] = (human_record, match_reason)

    for human_record in human_records:
        human_fields = human_record["fields"]
        paper_title = (
            human_fields.get("hasPaperTitle")
            or Path(human_record["path"]).stem
        )
        matches = matches_by_human_record[id(human_record)]
        if not matches:
            issues.append(
                {
                    "Issue type / 问题类型": "Missing KG instance / 缺少KG实例",
                    "Paper title / 论文标题": paper_title,
                    "Matched instance / 匹配实例": "",
                    "Detail / 说明": (
                        "No KG record matched this human Gold record by DOI or title / "
                        "未能通过DOI或标题为该人工Gold记录匹配KG实例"
                    ),
                }
            )
            continue
        if len(matches) > 1:
            instance_names = "; ".join(
                opf_record.get("local_name", "")
                for opf_record, _ in matches
            )
            issues.append(
                {
                    "Issue type / 问题类型": "Duplicate KG match / KG重复匹配",
                    "Paper title / 论文标题": paper_title,
                    "Matched instance / 匹配实例": instance_names,
                    "Detail / 说明": (
                        "Multiple KG records matched one human Gold record by DOI or title / "
                        "多个KG记录通过DOI或标题匹配到同一人工Gold记录"
                    ),
                }
            )
            continue

    # Preserve the established KG-title ordering of detail rows while using
    # the human Gold records as the fixed completeness and uniqueness guard.
    for opf_record in records:
        match = match_by_kg_record.get(id(opf_record))
        if match is None:
            continue
        human_record, match_reason = match
        if len(matches_by_human_record[id(human_record)]) != 1:
            continue
        human_fields = human_record["fields"]
        llm_fields = opf_record.get("data_properties", {})
        paper_title = (
            llm_fields.get("hasPaperTitle")
            or opf_record.get("local_name", "")
        )
        human_original_fields = human_record.get(
            "original_fields",
            human_fields,
        )
        matched_papers.append(
            {
                "record": opf_record,
                "human_record": human_record,
                "match_reason": match_reason,
            }
        )
        for field in SEMANTIC_DATA_PROPERTY_FIELDS:
            pairs.append(
                {
                    "Paper title / 论文标题": paper_title,
                    "Matched instance / 匹配实例": opf_record.get("local_name", ""),
                    "Human Gold file / 人工Gold文件": project_relative_path(
                        human_record["path"]
                    ),
                    "Match reason / 匹配方式": match_reason,
                    "Field / 字段": field,
                    "_human_value": clean_field_text(human_fields.get(field, "")),
                    "_human_original_value": clean_field_text(
                        human_original_fields.get(field, "")
                    ),
                    "_llm_value": clean_field_text(llm_fields.get(field, "")),
                }
            )
    return pairs, matched_papers, issues, extra_kg_records


def _score_field_pairs(
    pairs,
    model,
    progress_callback=None,
    force_factual_rejudgment=False,
):
    """Calculate similarity and obtain independent LLM factual judgments."""
    semantic_pair_indexes = []
    texts = []

    for index, pair in enumerate(pairs):
        gold_value = pair["_human_value"]
        llm_value = pair["_llm_value"]
        gold_missing = is_missing_field_value(gold_value)
        llm_missing = is_missing_field_value(llm_value)
        field = pair["Field / 字段"]

        if gold_missing or llm_missing:
            pair["_similarity"] = np.nan
            pair["_semantic_included"] = False
            pair["_semantic_method"] = "not_calculated"
            pair["_accuracy_included"] = False
            pair["_accurate"] = None
            if gold_missing and llm_missing:
                pair["_semantic_status"] = "skipped_both_values_missing"
                pair["_method"] = (
                    "skipped: both values absent / 跳过：双方字段均无值"
                )
                pair["_factual_reason"] = (
                    "双方均无可核验事实，因此不计入准确率 / "
                    "Neither side contains a factual claim, so this field is excluded from accuracy."
                )
            else:
                pair["_semantic_status"] = "skipped_one_sided_missing"
                pair["_method"] = (
                    "skipped: one-sided missing value / 跳过：单边字段缺失"
                )
                pair["_factual_reason"] = (
                    "Gold 与 LLM 仅一方有值，按评估规则跳过且不计入准确率 / "
                    "Only one side has a value; the field is skipped and excluded from accuracy."
                )
        elif field in EXACT_MATCH_FIELDS:
            exact = (
                semantic_normalize_identity_text(gold_value)
                == semantic_normalize_identity_text(llm_value)
            )
            pair["_similarity"] = 1.0 if exact else 0.0
            pair["_semantic_included"] = True
            pair["_semantic_method"] = "exact_identity_match"
            pair["_semantic_status"] = "compared"
            pair["_accuracy_included"] = True
        else:
            pair["_semantic_included"] = True
            pair["_semantic_method"] = "sentence_embedding_cosine"
            pair["_semantic_status"] = "compared"
            pair["_accuracy_included"] = True
            semantic_pair_indexes.append(index)
            texts.extend([gold_value, llm_value])

    if texts:
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=64,
            show_progress_bar=True,
        )
        for pair_position, pair_index in enumerate(semantic_pair_indexes):
            gold_embedding = embeddings[pair_position * 2]
            llm_embedding = embeddings[pair_position * 2 + 1]
            similarity = float(np.dot(gold_embedding, llm_embedding))
            pairs[pair_index]["_similarity"] = float(
                np.clip(similarity, 0.0, 1.0)
            )

    cache = load_field_factual_judgment_cache()
    pairs_by_paper = {}
    for pair in pairs:
        key = (
            pair["Paper title / 论文标题"],
            pair["Matched instance / 匹配实例"],
        )
        pairs_by_paper.setdefault(key, []).append(pair)

    total_papers = len(pairs_by_paper)
    for paper_index, paper_pairs in enumerate(
        pairs_by_paper.values(),
        start=1,
    ):
        comparable_pairs = [
            pair
            for pair in paper_pairs
            if pair.get("_accuracy_included")
        ]
        if not comparable_pairs:
            continue
        cache_key = _field_judgment_cache_key(paper_pairs)
        source_hash = _field_judgment_source_hash(comparable_pairs)
        cached = cache["records"].get(cache_key, {})
        cached_judgments = cached.get("judgments", {})
        expected_fields = {
            pair["Field / 字段"]
            for pair in comparable_pairs
        }
        cached_field_pairs = [
            pair
            for pair in paper_pairs
            if pair["Field / 字段"] in cached_judgments
        ]
        cached_source_still_matches = (
            bool(cached_field_pairs)
            and cached.get("source_hash")
            == _field_judgment_source_hash(cached_field_pairs)
        )
        cache_valid = (
            not force_factual_rejudgment
            and expected_fields.issubset(cached_judgments)
            and (
                cached.get("source_hash") == source_hash
                or cached_source_still_matches
            )
        )
        if cache_valid:
            judgments = cached_judgments
            cache_state_en = "cached"
            cache_state_zh = "使用缓存"
        else:
            judgments = judge_paper_fields_with_llm(comparable_pairs)
            cache["records"][cache_key] = {
                "source_hash": source_hash,
                "paper_title": paper_pairs[0]["Paper title / 论文标题"],
                "instance_name": paper_pairs[0]["Matched instance / 匹配实例"],
                "judgments": judgments,
            }
            save_field_factual_judgment_cache(cache)
            cache_state_en = "judged by LLM"
            cache_state_zh = "已由LLM判定"

        for pair in comparable_pairs:
            field = pair["Field / 字段"]
            judgment = judgments[field]
            pair["_accurate"] = bool(judgment["factually_correct"])
            pair["_factual_reason"] = clean_field_text(judgment["reason"])
            pair["_method"] = (
                "LLM factual judgment; similarity not used / "
                "LLM事实判定；不使用相似度阈值"
            )

        if progress_callback is not None:
            progress = 58 + int(28 * paper_index / max(total_papers, 1))
            progress_callback(
                progress,
                (
                    f"LLM factual field judgment {paper_index}/{total_papers} "
                    f"({cache_state_en})"
                ),
                (
                    f"LLM字段事实判定 {paper_index}/{total_papers}"
                    f"（{cache_state_zh}）"
                ),
            )

    rows = []
    for pair in pairs:
        accuracy_included = bool(pair.get("_accuracy_included"))
        field_code = pair["Field / 字段"]
        field_label_en, field_label_zh = FIELD_LABELS[field_code]
        rows.append(
            {
                "paper_title": pair["Paper title / 论文标题"],
                "model_instance": pair["Matched instance / 匹配实例"],
                "field_code": field_code,
                "field_label_en": field_label_en,
                "field_label_zh": field_label_zh,
                "semantic_similarity": pair["_similarity"],
                "included_in_semantic_similarity": bool(
                    pair.get("_semantic_included")
                ),
                "semantic_method": pair["_semantic_method"],
                "semantic_status": pair["_semantic_status"],
                "included_in_factual_accuracy": accuracy_included,
                "factually_accurate": (
                    bool(pair["_accurate"])
                    if accuracy_included
                    else pd.NA
                ),
                "factual_judgment_reason": single_line_text(
                    pair["_factual_reason"]
                ),
                "factual_status": pair["_method"],
                "human_gold_original_value": single_line_text(
                    pair["_human_original_value"]
                ),
                "human_gold_english_value": single_line_text(
                    pair["_human_value"]
                ),
                "kg_llm_value": single_line_text(pair["_llm_value"]),
                "human_gold_file": pair["Human Gold file / 人工Gold文件"],
                "match_method": pair["Match reason / 匹配方式"],
            }
        )
    return rows


SEMANTIC_DETAIL_COLUMNS = [
    "paper_title",
    "model_instance",
    "field_code",
    "field_label_en",
    "field_label_zh",
    "included_in_semantic_similarity",
    "semantic_similarity",
    "semantic_method",
    "semantic_status",
    "human_gold_original_value",
    "human_gold_english_value",
    "kg_llm_value",
    "human_gold_file",
    "match_method",
]

FACTUAL_DETAIL_COLUMNS = [
    "paper_title",
    "model_instance",
    "field_code",
    "field_label_en",
    "field_label_zh",
    "included_in_factual_accuracy",
    "factually_accurate",
    "factual_judgment_reason",
    "factual_status",
    "human_gold_original_value",
    "human_gold_english_value",
    "kg_llm_value",
    "human_gold_file",
    "match_method",
]


def build_paper_ingestion_validation_outputs(
    field_df,
    kg_record_count,
    human_record_count,
    matched_paper_count,
):
    """Split field judgments into two readable details tables and one summary."""
    semantic_df = field_df[SEMANTIC_DETAIL_COLUMNS].copy()
    factual_df = field_df[FACTUAL_DETAIL_COLUMNS].copy()

    semantic_mask = semantic_df["included_in_semantic_similarity"].astype(bool)
    factual_mask = factual_df["included_in_factual_accuracy"].astype(bool)
    configured_field_count = int(len(field_df))
    semantic_field_count = int(semantic_mask.sum())
    factual_field_count = int(factual_mask.sum())
    accurate_field_count = int(
        factual_df.loc[factual_mask, "factually_accurate"].eq(True).sum()
    )
    one_sided_missing_count = int(
        semantic_df["semantic_status"].eq("skipped_one_sided_missing").sum()
    )
    both_missing_count = int(
        semantic_df["semantic_status"].eq("skipped_both_values_missing").sum()
    )
    skipped_field_count = configured_field_count - factual_field_count

    summary_df = pd.DataFrame(
        [
            {
                "validation_status": "passed",
                "knowledge_graph_record_count": int(kg_record_count),
                "human_gold_record_count": int(human_record_count),
                "matched_paper_count": int(matched_paper_count),
                "configured_field_count_per_paper": len(
                    SEMANTIC_DATA_PROPERTY_FIELDS
                ),
                "configured_field_pair_count": configured_field_count,
                "semantic_compared_field_count": semantic_field_count,
                "overall_average_semantic_similarity": float(
                    semantic_df.loc[semantic_mask, "semantic_similarity"].mean()
                ),
                "factual_evaluated_field_count": factual_field_count,
                "factually_accurate_field_count": accurate_field_count,
                "factually_inaccurate_field_count": (
                    factual_field_count - accurate_field_count
                ),
                "overall_factual_accuracy": (
                    accurate_field_count / factual_field_count
                    if factual_field_count
                    else np.nan
                ),
                "skipped_field_count": skipped_field_count,
                "one_sided_missing_field_count": one_sided_missing_count,
                "both_missing_field_count": both_missing_count,
                "semantic_model": SEMANTIC_MODEL_NAME,
                "factual_judgment_model": MODEL_NAME,
                "gold_comparison_language": "English",
                "semantic_method": (
                    "Exact match for title/year/DOI; multilingual sentence-"
                    "embedding cosine similarity for all other comparable fields."
                ),
                "factual_accuracy_method": (
                    "LLM field-level factual judgment against the human Gold; "
                    "missing fields are excluded from the denominator."
                ),
            }
        ]
    )
    return semantic_df, factual_df, summary_df


def run_paper_ingestion_semantic_validation(
    max_papers=None,
    model_name=SEMANTIC_MODEL_NAME,
    save=True,
    extra_human_dirs=None,
    progress_callback=None,
    translate_human_gold=True,
    force_gold_retranslation=False,
    force_factual_rejudgment=False,
):
    """Compare English LLM PaperModels with English-translated human Gold.

    Returns:
        semantic_df: field-level semantic-similarity details.
        factual_df: field-level factual-accuracy details.
        summary_df: one-row overall validation summary.
    """
    def report(progress, message_en, message_zh):
        if progress_callback is not None:
            progress_callback(progress, message_en, message_zh)

    report(
        5,
        "Loading 35 human-curated Gold records",
        "正在加载35篇人工Gold记录",
    )
    human_records = collect_human_paper_record_markdowns(
        extra_dirs=extra_human_dirs
    )
    report(
        10,
        "Reading LLM-ingested PaperModel records from the knowledge graph",
        "正在从知识图谱读取LLM录入的PaperModel记录",
    )
    kg_records = read_opfmodel_data_records_for_similarity()
    if translate_human_gold:
        report(
            12,
            "Preparing faithful English translations of human Gold records",
            "正在准备人工Gold记录的保真英文翻译",
        )
        human_records = translate_human_gold_records_to_english(
            human_records,
            force=force_gold_retranslation,
            progress_callback=report,
        )
    report(
        38,
        "Matching Gold records and LLM records by DOI and paper title",
        "正在通过DOI和论文标题匹配Gold记录与LLM记录",
    )
    pairs, matched_papers, issue_rows, extra_kg_records = _build_field_pairs(
        kg_records,
        human_records,
        max_papers=max_papers,
    )

    if issue_rows:
        issue_titles = "; ".join(
            str(issue.get("Paper title / 论文标题", ""))
            for issue in issue_rows
        )
        raise RuntimeError(
            "论文录入验证发现人工Gold缺少KG实例或KG重复匹配，已停止生成结果："
            f"{issue_titles} / Paper-ingestion validation found missing or "
            "duplicate KG matches for the fixed human Gold benchmark and "
            f"stopped: {issue_titles}"
        )

    if extra_kg_records:
        extra_instance_names = "; ".join(
            record.get("local_name", "")
            for record in extra_kg_records
        )
        print(
            "Ignoring KG records outside the fixed human Gold benchmark:",
            extra_instance_names,
        )
        report(
            40,
            "Ignoring extra KG records without human Gold: "
            + extra_instance_names,
            "已忽略没有人工Gold的额外KG记录："
            + extra_instance_names,
        )

    if not pairs:
        raise RuntimeError(
            "没有匹配到可评估的人工Gold与LLM记录 / "
            "No matched human-Gold and LLM records were found."
        )

    print(
        "匹配论文 / Matched papers:",
        len(matched_papers),
        "| 评估字段 / Field judgments:",
        len(pairs),
    )
    report(
        42,
        "Loading the multilingual sentence-embedding model",
        "正在加载多语言句向量模型",
    )
    model = load_sentence_transformer_model(model_name)
    report(
        50,
        f"Calculating semantic similarity for {len(pairs)} field pairs",
        f"正在计算{len(pairs)}组字段的语义相似度",
    )
    field_rows = _score_field_pairs(
        pairs,
        model,
        progress_callback=report,
        force_factual_rejudgment=force_factual_rejudgment,
    )
    field_df = pd.DataFrame(field_rows)

    report(
        88,
        "Building two field-detail tables and the overall summary",
        "正在生成两份字段明细表和总体汇总表",
    )
    semantic_df, factual_df, summary_df = (
        build_paper_ingestion_validation_outputs(
            field_df,
            kg_record_count=len(kg_records),
            human_record_count=len(human_records),
            matched_paper_count=len(matched_papers),
        )
    )

    if len(semantic_df) != len(factual_df):
        raise RuntimeError(
            "语义明细与事实明细行数不一致 / Semantic and factual detail "
            "tables have different row counts."
        )
    if len(matched_papers) != len(human_records):
        raise RuntimeError(
            "人工Gold和唯一匹配论文数量不一致，已停止保存结果 / "
            "Human Gold and uniquely matched-paper counts differ; results were not saved."
        )

    if save:
        report(
            92,
            "Saving semantic details, factual details, and the overall summary",
            "正在保存语义明细、事实明细和总体汇总",
        )
        PAPER_INGESTION_VALIDATION_REPORTS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )
        semantic_df.to_csv(
            PAPER_INGESTION_SEMANTIC_SIMILARITY_DETAILS_CSV,
            index=False,
            encoding="utf-8-sig",
        )
        factual_df.to_csv(
            PAPER_INGESTION_FACTUAL_ACCURACY_DETAILS_CSV,
            index=False,
            encoding="utf-8-sig",
        )
        summary_df.to_csv(
            PAPER_INGESTION_VALIDATION_SUMMARY_CSV,
            index=False,
            encoding="utf-8-sig",
        )
        print(
            "已保存论文录入验证结果 / Saved paper-ingestion validation:",
            PAPER_INGESTION_QUALITY_VALIDATION_DIR,
        )

    report(
        100,
        "Paper-ingestion validation completed",
        "论文录入验证已完成",
    )
    return semantic_df, factual_df, summary_df
