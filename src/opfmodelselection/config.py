from pathlib import Path
import os
import json
import warnings
import time
import copy
import math

import numpy as np
import pandas as pd

try:
    from owlready2 import *  # noqa: F401,F403
except ImportError:
    # Some online recommendation functions only use RDF/XML directly.
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_BASE = PROJECT_ROOT / "data"
PROMPT_CATALOG_PATH = PROJECT_ROOT / "prompts.toml"

# All project data and generated artifacts are grouped by workflow and stage.
# Runtime artifacts such as the PaperModel KG have one canonical file. The
# public paper bibliography is the deliberate exception: workflow 01 owns the
# editable canonical CSV, while workflow 02 keeps a byte-checked citation mirror.
PAPER_INGESTION_WORKFLOW_DIR = DATA_BASE / "01_paper_ingestion_workflow"
PAPER_INGESTION_INPUT_DIR = PAPER_INGESTION_WORKFLOW_DIR / "01_input"
PAPER_DIR = PAPER_INGESTION_INPUT_DIR / "01_source_papers"
PAPER_INGESTION_INTERMEDIATE_DIR = PAPER_INGESTION_WORKFLOW_DIR / "02_intermediate"
PAPER_PROCESSING_OUTPUT_DIR = (
    PAPER_INGESTION_INTERMEDIATE_DIR / "01_pdf_processing_outputs"
)
PAPER_INGESTION_OUTPUT_DIR = PAPER_INGESTION_WORKFLOW_DIR / "03_output"

ONLINE_RECOMMENDATION_WORKFLOW_DIR = (
    DATA_BASE / "02_online_recommendation_workflow"
)
ONLINE_RECOMMENDATION_INPUT_DIR = (
    ONLINE_RECOMMENDATION_WORKFLOW_DIR / "01_input"
)
ONLINE_USER_REQUIREMENTS_CSV = (
    ONLINE_RECOMMENDATION_INPUT_DIR / "01_user_requirements.csv"
)
ONLINE_REQUIREMENT_SOURCE_TRACEABILITY_DIR = (
    ONLINE_RECOMMENDATION_INPUT_DIR / "02_requirement_source_traceability"
)
ENTERPRISE_REQUIREMENT_SOURCE_REPORTS_DIR = (
    ONLINE_REQUIREMENT_SOURCE_TRACEABILITY_DIR / "01_enterprise_grid_reports"
)
ENTERPRISE_GRID_REPORTS_MANIFEST_CSV = (
    ENTERPRISE_REQUIREMENT_SOURCE_REPORTS_DIR
    / "enterprise_grid_reports_manifest.csv"
)
PAPER_CORPUS_MANIFEST_PATH = PAPER_DIR / "paper_corpus_manifest.csv"
PAPER_CORPUS_MANIFEST_MIRROR_PATH = (
    ONLINE_REQUIREMENT_SOURCE_TRACEABILITY_DIR / "02_paper_corpus_manifest.csv"
)
ONLINE_RECOMMENDATION_INTERMEDIATE_DIR = (
    ONLINE_RECOMMENDATION_WORKFLOW_DIR / "02_intermediate"
)
ONLINE_RECOMMENDATION_OUTPUT_DIR = (
    ONLINE_RECOMMENDATION_WORKFLOW_DIR / "03_output"
)

VALIDATION_WORKFLOW_DIR = DATA_BASE / "03_validation"
VALIDATION_INPUT_DIR = VALIDATION_WORKFLOW_DIR / "01_input"
VALIDATION2_HUMAN_GOLD_DIR = (
    VALIDATION_INPUT_DIR / "01_recommendation_human_gold"
)
HUMAN_PAPER_MODEL_GOLD_DIR = (
    VALIDATION_INPUT_DIR / "02_paper_ingestion_human_gold"
)
HUMAN_PAPER_MODEL_RECORD_DIR = HUMAN_PAPER_MODEL_GOLD_DIR / "01_records"
VALIDATION_INTERMEDIATE_DIR = VALIDATION_WORKFLOW_DIR / "02_intermediate"
PAPER_INGESTION_VALIDATION_CACHE_DIR = (
    VALIDATION_INTERMEDIATE_DIR / "01_llm_validation_cache"
)
SENTENCE_TRANSFORMERS_CACHE_DIR = (
    VALIDATION_INTERMEDIATE_DIR / "02_semantic_embedding_model_cache"
)
VALIDATION_OUTPUT_DIR = VALIDATION_WORKFLOW_DIR / "03_output"
RECOMMENDATION_VALIDATION_RESULTS_DIR = (
    VALIDATION_OUTPUT_DIR / "01_recommendation_validation"
)
PAPER_INGESTION_VALIDATION_RESULTS_DIR = (
    VALIDATION_OUTPUT_DIR / "02_paper_ingestion_validation"
)
PAPER_INGESTION_VALIDATION_REPORTS_DIR = PAPER_INGESTION_VALIDATION_RESULTS_DIR

# Canonical namespace for the Bocheng Xu OPF ontology and integrated PaperModel KG.
# Keep it in one place so readers and writers cannot silently drift apart.
OPF_ONTOLOGY_IRI = "http://www.semanticweb.org/bochengxu/OPF_Ontology"
OPF_IRI = OPF_ONTOLOGY_IRI + "#"
OPF_KNOWLEDGE_GRAPH_IRI = OPF_ONTOLOGY_IRI + "/knowledge-graph"
# Backward-compatible name. There is one integrated knowledge graph rather
# than a separate instance-only ontology.
OPF_INSTANCE_ONTOLOGY_IRI = OPF_KNOWLEDGE_GRAPH_IRI

BASE_OWL_PATH = PROJECT_ROOT / "ontology" / "OPF_Ontology2.0.owl"
KNOWLEDGE_GRAPH_OWL_PATH = (
    PAPER_INGESTION_OUTPUT_DIR / "OPF_Knowledge_Graph2.0.owl"
)
# Backward-compatible alias used by existing notebook code. It now points to
# the integrated knowledge graph file, not to a separate instance-only file.
INSTANCE_OWL_PATH = KNOWLEDGE_GRAPH_OWL_PATH
CIM_OWL_PATH = (
    PROJECT_ROOT
    / "ontology"
    / "IEC-CIM-Ontology-main"
    / "IEC-CIM-Ontology-main"
    / "TheCimOntology.owl"
)
OEO_OWL_PATH = PROJECT_ROOT / "ontology" / "oeo-2.11.0" / "oeo.owl"
OEO_MODEL_OWL_PATH = PROJECT_ROOT / "ontology" / "oeo-2.11.0" / "modules" / "oeo-model.owl"
OEO_IMPORTS_DIR = PROJECT_ROOT / "ontology" / "oeo-2.11.0" / "imports"

RECOMMENDATION_HUMAN_GOLD_CSV = (
    VALIDATION2_HUMAN_GOLD_DIR / "recommendation_human_gold_54_requirements.csv"
)

OPENAI_MODEL_NAME = "gpt-5.4-mini"
RWTH_MODEL_NAME = "mistralai-mistral-small-4-119b"
USE_OPENAI_HARD_SCHEMA = True
LLM_TEMPERATURE = 0
LLM_API_TEMPERATURE = 0
LIST_RWTH_MODELS = False

# Token-budget guardrail used before every wrapped LLM API call.
# These are configurable project guardrails, not guaranteed official model limits.
GPT54MINI_CONTEXT_TOKENS = int(os.environ.get("GPT54MINI_CONTEXT_TOKENS", "128000"))
DEFAULT_MODEL_CONTEXT_TOKENS = int(os.environ.get("DEFAULT_MODEL_CONTEXT_TOKENS", "128000"))
DEFAULT_RESERVED_OUTPUT_TOKENS = int(os.environ.get("DEFAULT_RESERVED_OUTPUT_TOKENS", "8000"))
MODEL_TOKEN_BUDGETS = {
    "gpt-5.4-mini": {
        "context_tokens": GPT54MINI_CONTEXT_TOKENS,
    },
    "mistralai-mistral-small-4-119b": {
        "context_tokens": int(os.environ.get("RWTH_MODEL_CONTEXT_TOKENS", "128000")),
    },
}
LLM_CALL_DIAGNOSTICS = []

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
RWTH_API_KEY = os.environ.get("RWTH_API_KEY")

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OpenAI and OPENAI_API_KEY else None
rwth_client = (
    OpenAI(api_key=RWTH_API_KEY, base_url="https://chat.kiconnect.nrw/api/v1")
    if OpenAI and RWTH_API_KEY
    else None
)

if USE_OPENAI_HARD_SCHEMA:
    client = openai_client
    MODEL_NAME = OPENAI_MODEL_NAME
    LLM_PIPELINE_NAME = "OpenAI hard-schema multimodal pipeline"
else:
    client = rwth_client
    MODEL_NAME = RWTH_MODEL_NAME
    LLM_PIPELINE_NAME = "RWTH soft-prompt text pipeline"


def print_llm_config_status():
    print("统一 LLM/API 配置已加载 / Shared LLM/API configuration loaded.")
    print("当前路线 / Active pipeline:", LLM_PIPELINE_NAME)
    print("OpenAI 模型 / OPENAI_MODEL_NAME:", OPENAI_MODEL_NAME)
    print("RWTH 模型 / RWTH_MODEL_NAME:", RWTH_MODEL_NAME)
    print("temperature / 温度:", LLM_TEMPERATURE)
    print("强制 API temperature / forced API temperature:", LLM_API_TEMPERATURE)
    active_budget = get_model_token_budget(MODEL_NAME)
    print("模型上下文 token 上限 / model context token limit:", active_budget["context_tokens"])
    print("预留输出 token / reserved output tokens:", active_budget["reserved_output_tokens"])
    print("OPENAI_API_KEY 是否存在 / available:", bool(OPENAI_API_KEY))
    print("RWTH_API_KEY 是否存在 / available:", bool(RWTH_API_KEY))
    if USE_OPENAI_HARD_SCHEMA and openai_client is None:
        print("警告：当前选择 OpenAI 路线，但没有 OPENAI_API_KEY。真正调用 LLM 时会报错。")
    if (not USE_OPENAI_HARD_SCHEMA) and rwth_client is None:
        print("警告：当前选择 RWTH 路线，但没有 RWTH_API_KEY。真正调用 LLM 时会报错。")
    if LIST_RWTH_MODELS and rwth_client is not None:
        print("RWTH 可用模型 / available RWTH models:")
        for model in rwth_client.models.list().data:
            print("  -", model.id)


def get_model_token_budget(model_name=None, reserved_output_tokens=None):
    """Return configured context and reserved-output budget for one model."""
    model_name = model_name or MODEL_NAME
    budget = MODEL_TOKEN_BUDGETS.get(
        model_name,
        {
            "context_tokens": DEFAULT_MODEL_CONTEXT_TOKENS,
        },
    )
    context_tokens = int(budget.get("context_tokens", DEFAULT_MODEL_CONTEXT_TOKENS))
    reserved = int(reserved_output_tokens or DEFAULT_RESERVED_OUTPUT_TOKENS)
    return {
        "model_name": model_name,
        "context_tokens": context_tokens,
        "reserved_output_tokens": reserved,
    }


def estimate_text_tokens(text, model_name=None):
    """Estimate tokens. Uses tiktoken when available, otherwise a conservative chars/4 fallback."""
    text = "" if text is None else str(text)
    try:
        import tiktoken  # type: ignore

        try:
            encoding = tiktoken.encoding_for_model(model_name or MODEL_NAME)
        except Exception:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return max(1, math.ceil(len(text) / 4))


def estimate_messages_tokens(messages, model_name=None):
    payload = json.dumps(messages or [], ensure_ascii=False, default=str)
    # Add a small envelope allowance for chat message roles and separators.
    return estimate_text_tokens(payload, model_name=model_name) + max(len(messages or []) * 4, 0)


def reset_llm_call_diagnostics():
    LLM_CALL_DIAGNOSTICS.clear()


def get_llm_call_diagnostics():
    return list(LLM_CALL_DIAGNOSTICS)


def check_llm_input_budget(
    messages,
    model_name=None,
    call_name="LLM call",
    reserved_output_tokens=None,
    record=True,
):
    """Check prompt size before an LLM call and record a GUI-readable diagnostic row."""
    budget = get_model_token_budget(model_name=model_name, reserved_output_tokens=reserved_output_tokens)
    estimated_input_tokens = estimate_messages_tokens(messages, model_name=budget["model_name"])
    prompt_chars = len(json.dumps(messages or [], ensure_ascii=False, default=str))
    over_context_limit = estimated_input_tokens + budget["reserved_output_tokens"] > budget["context_tokens"]
    if over_context_limit:
        level = "error"
        message = (
            "输入可能超过模型上下文窗口，API 很可能报错。"
            " / Input may exceed the model context window and the API is likely to fail."
        )
    else:
        level = "ok"
        message = "输入长度未超过配置的上下文窗口。 / Input length is within the configured context window."
    diagnostic = {
        "call_name": call_name,
        "model_name": budget["model_name"],
        "prompt_chars": prompt_chars,
        "estimated_input_tokens": estimated_input_tokens,
        "reserved_output_tokens": budget["reserved_output_tokens"],
        "context_tokens": budget["context_tokens"],
        "level": level,
        "over_context_limit": over_context_limit,
        "message": message,
    }
    if record:
        LLM_CALL_DIAGNOSTICS.append(diagnostic)
    if level != "ok":
        print(
            f"[LLM input budget / LLM 输入预算] {call_name}: "
            f"input={estimated_input_tokens}, reserved_output={budget['reserved_output_tokens']}, "
            f"context={budget['context_tokens']}. {message}"
        )
    return diagnostic

def check_project_paths(include_oeo_model=True):
    paths = {
        "DATA_BASE": DATA_BASE,
        "PROMPT_CATALOG_PATH": PROMPT_CATALOG_PATH,
        "PAPER_CORPUS_MANIFEST_PATH": PAPER_CORPUS_MANIFEST_PATH,
        "PAPER_CORPUS_MANIFEST_MIRROR_PATH": PAPER_CORPUS_MANIFEST_MIRROR_PATH,
        "PAPER_DIR": PAPER_DIR,
        "HUMAN_PAPER_MODEL_RECORD_DIR": HUMAN_PAPER_MODEL_RECORD_DIR,
        "RECOMMENDATION_HUMAN_GOLD_CSV": RECOMMENDATION_HUMAN_GOLD_CSV,
        "ENTERPRISE_REQUIREMENT_SOURCE_REPORTS_DIR": (
            ENTERPRISE_REQUIREMENT_SOURCE_REPORTS_DIR
        ),
        "ENTERPRISE_GRID_REPORTS_MANIFEST_CSV": (
            ENTERPRISE_GRID_REPORTS_MANIFEST_CSV
        ),
        "ONLINE_USER_REQUIREMENTS_CSV": ONLINE_USER_REQUIREMENTS_CSV,
        "BASE_OWL_PATH": BASE_OWL_PATH,
        "KNOWLEDGE_GRAPH_OWL_PATH": KNOWLEDGE_GRAPH_OWL_PATH,
        "CIM_OWL_PATH": CIM_OWL_PATH,
        "OEO_OWL_PATH": OEO_OWL_PATH,
    }
    if include_oeo_model:
        paths["OEO_MODEL_OWL_PATH"] = OEO_MODEL_OWL_PATH
        paths["OEO_IMPORTS_DIR"] = OEO_IMPORTS_DIR
    for name, path in paths.items():
        print(f"{name} 路径 / path =", path)
        print("是否存在 / exists:", path.exists())
        print()
    for name, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"{name} not found: {path}")
    if (
        PAPER_CORPUS_MANIFEST_PATH.read_bytes()
        != PAPER_CORPUS_MANIFEST_MIRROR_PATH.read_bytes()
    ):
        raise ValueError(
            "Paper corpus manifest mirror is out of sync. Update the canonical "
            f"file at {PAPER_CORPUS_MANIFEST_PATH} and copy it byte-for-byte to "
            f"{PAPER_CORPUS_MANIFEST_MIRROR_PATH}."
        )
    return paths


def project_relative_path(value):
    """Return a portable project-relative POSIX path whenever possible."""
    if not value:
        return ""
    raw = Path(str(value))
    candidate = raw if raw.is_absolute() else PROJECT_ROOT / raw
    try:
        return candidate.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        return raw.as_posix()


def make_project_paths_portable(value):
    """Recursively store project paths as portable, POSIX-style relative paths."""
    if isinstance(value, dict):
        return {
            key: make_project_paths_portable(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [make_project_paths_portable(item) for item in value]
    if isinstance(value, tuple):
        return tuple(make_project_paths_portable(item) for item in value)
    if isinstance(value, Path):
        return project_relative_path(value)
    if isinstance(value, str):
        portable = value.replace(f"{PROJECT_ROOT}\\", "")
        portable = portable.replace(f"{PROJECT_ROOT.as_posix()}/", "")
        # Path values can also be embedded in a prompt or log line. Normalize
        # only lines that contain a known project-relative prefix so ordinary
        # prose, regular expressions, and mathematical backslashes stay intact.
        project_prefixes = ("data\\", "src\\", "ontology\\", "Figure\\")
        normalized_lines = []
        for line in portable.splitlines(keepends=True):
            if any(prefix in line for prefix in project_prefixes):
                line = line.replace("\\", "/")
            normalized_lines.append(line)
        return "".join(normalized_lines)
    return value


def resolve_instance_owl_read_path():
    """Return the one canonical PaperModel KG, failing loudly if it is missing."""
    if not INSTANCE_OWL_PATH.exists():
        raise FileNotFoundError(
            "Canonical PaperModel knowledge graph not found: "
            f"{INSTANCE_OWL_PATH}"
        )
    return INSTANCE_OWL_PATH


def read_opf_xml():
    from xml.etree import ElementTree as ET

    xml_text = BASE_OWL_PATH.read_text(encoding="utf-8")
    xml_root = ET.fromstring(xml_text)
    owl_imports = [elem.attrib for elem in xml_root.iter() if elem.tag.endswith("}imports")]
    return xml_text, xml_root, owl_imports


def read_instance_xml():
    from xml.etree import ElementTree as ET

    read_path = resolve_instance_owl_read_path()
    xml_text = read_path.read_text(encoding="utf-8")
    xml_root = ET.fromstring(xml_text)
    owl_imports = [elem.attrib for elem in xml_root.iter() if elem.tag.endswith("}imports")]
    return xml_text, xml_root, owl_imports


def print_opf_xml_status():
    schema_text, _, schema_imports = read_opf_xml()
    kg_text, _, kg_imports = read_instance_xml()
    kg_read_path = resolve_instance_owl_read_path()
    print("已读取 OPF 本体框架 XML / Loaded OPF ontology framework XML:")
    print("本体文件路径 / Ontology OWL file path:", BASE_OWL_PATH)
    print("本体框架 XML 字符数 / Framework XML characters:", len(schema_text))
    print("本体框架 owl:imports 数量 / Framework owl:imports count:", len(schema_imports))
    print("已读取 OPF 知识图谱 XML / Loaded OPF knowledge graph XML:")
    print("知识图谱目标路径 / Knowledge graph target path:", KNOWLEDGE_GRAPH_OWL_PATH)
    print("当前实际读取路径 / Current read path:", kg_read_path)
    print("知识图谱 XML 字符数 / Knowledge graph XML characters:", len(kg_text))
    print("知识图谱 owl:imports 数量 / Knowledge graph owl:imports count:", len(kg_imports))
    if schema_imports:
        print("提醒：当前本体框架含 owl:imports，请确认没有重新引入整本 OEO/CIM。")
    return schema_text, schema_imports

def setup_owlready_paths(include_oeo_model=True):
    try:
        onto_path  # noqa: B018,F821
    except NameError as exc:
        raise RuntimeError("owlready2 is not available in this environment.") from exc

    def add_onto_path(folder: Path):
        folder_str = str(folder)
        if folder_str not in onto_path:  # noqa: F405
            onto_path.append(folder_str)  # noqa: F405

    add_onto_path(BASE_OWL_PATH.parent)
    add_onto_path(CIM_OWL_PATH.parent)
    add_onto_path(OEO_OWL_PATH.parent)
    if include_oeo_model:
        add_onto_path(OEO_MODEL_OWL_PATH.parent)
        add_onto_path(OEO_IMPORTS_DIR)

    cim_file = str(CIM_OWL_PATH)
    oeo_file = str(OEO_OWL_PATH)
    PREDEFINED_ONTOLOGIES["http://www.iec.ch/TC57/CIM#"] = cim_file  # noqa: F405
    PREDEFINED_ONTOLOGIES["http://www.iec.ch/TC57/CIM"] = cim_file  # noqa: F405
    PREDEFINED_ONTOLOGIES["http://www.iec.ch/TC57/CIM/"] = cim_file  # noqa: F405
    PREDEFINED_ONTOLOGIES["https://openenergyplatform.org/ontology/oeo/releases/2.11.0/oeo.omn"] = oeo_file  # noqa: F405
    PREDEFINED_ONTOLOGIES["https://openenergyplatform.org/ontology/oeo/releases/2.11.0/oeo.owl"] = oeo_file  # noqa: F405
    PREDEFINED_ONTOLOGIES["https://openenergyplatform.org/ontology/oeo/"] = oeo_file  # noqa: F405

    if include_oeo_model:
        oeo_model_file = str(OEO_MODEL_OWL_PATH)
        PREDEFINED_ONTOLOGIES["https://openenergyplatform.org/ontology/oeo/releases/2.11.0/oeo-model.omn"] = oeo_model_file  # noqa: F405
        PREDEFINED_ONTOLOGIES["https://openenergyplatform.org/ontology/oeo/releases/2.11.0/oeo-model.owl"] = oeo_model_file  # noqa: F405
        for module_owl_path in OEO_MODEL_OWL_PATH.parent.glob("*.owl"):
            module_name = module_owl_path.stem
            module_file = str(module_owl_path)
            PREDEFINED_ONTOLOGIES[f"https://openenergyplatform.org/ontology/oeo/releases/2.11.0/{module_name}.owl"] = module_file  # noqa: F405
            PREDEFINED_ONTOLOGIES[f"https://openenergyplatform.org/ontology/oeo/releases/2.11.0/{module_name}.omn"] = module_file  # noqa: F405
        for import_owl_path in OEO_IMPORTS_DIR.glob("*.owl"):
            import_name = import_owl_path.name
            PREDEFINED_ONTOLOGIES[f"https://openenergyplatform.org/ontology/oeo/releases/2.11.0/imports/{import_name}"] = str(import_owl_path)  # noqa: F405
