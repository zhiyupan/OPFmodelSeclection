"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *
from .pdf_processing import *
from .paper_writer import *
from .prompt_loader import render_prompt

# 8.9.1 Look up the OPFModel instance already written to the knowledge graph for the current PAPER_PATH.
# Read only OPF_Knowledge_Graph2.0.owl and source-paper metadata; do not modify the schema ontology or knowledge graph.

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path

RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDF_ABOUT = "{" + RDF_NS + "}about"
RDF_RESOURCE = "{" + RDF_NS + "}resource"
RDF_DATATYPE = "{" + RDF_NS + "}datatype"

PAPERMODEL_PRINT_SECTIONS = [
    (
        "1. PaperMetadata / 论文与模型基础识别信息",
        [
            ("hasModelName", "模型名称"),
            ("hasPaperTitle", "论文标题"),
            ("hasPublicationYear", "发表年份"),
            ("hasDOI", "DOI 编号"),
            ("hasAuthor", "作者"),
            ("hasInstitution", "作者机构 / 研究机构"),
        ],
    ),
    (
        "2. MotivationAndSolvedProblem / 模型提出动机与解决的问题",
        [
            ("hasPrimaryPurpose", "这个模型主要用来干什么"),
            ("hasMotivation", "为什么论文要提出这个模型"),
            ("hasSolvedProblem", "这个模型具体解决了什么问题"),
            ("hasResearchQuestion", "论文研究问题"),
            ("hasPrimaryOutput", "这个模型最后主要输出什么类型的结果"),
        ],
    ),
    (
        "3. ModelFeature / 模型特征标签",
        [
            ("hasModelFeature", "总模型特征父属性"),
            ("hasPowerFlowFormulationFeature", "潮流建模特征"),
            ("hasTimeHorizonFeature", "时间建模特征"),
            ("hasTemporalResolution", "时间分辨率 / 时间步长"),
            ("hasOptimizationHorizon", "优化时域 / 一次优化覆盖的总时长"),
            ("hasUncertaintyHandlingFeature", "不确定性处理特征"),
            ("hasPowerSystemDomainFeature", "电力系统对象 / 应用域特征"),
            ("hasSolutionMethodEnhancementFeature", "求解方法增强特征"),
            ("hasModelPerformanceFeature", "模型性能倾向特征"),
            ("hasDemandSideFeature", "用户侧 / 需求侧建模特征"),
        ],
    ),
    (
        "4. ModelStructure DataProperties / 模型结构信息：数据属性",
        [
            ("hasObjectiveFunction", "目标函数文本摘要"),
            ("hasConstraintFunction", "约束函数文本摘要"),
            ("usesParameter", "使用的参数变量文本摘要"),
            ("hasSolutionDetailsSummary", "求解细节 summary"),
            ("hasModelValidationSummary", "实验设置 summary"),
            ("hasFindingsSummary", "验证表现、对比结果与论文结论 summary"),
            ("hasStrengthsAndLimitationsSummary", "优点与限制 summary"),
            ("isScenarioSuitability", "多场景适用性 / Monte-Carlo 相关布尔值"),
            ("hasFurtherProperty", "其他补充信息"),
        ],
    ),
]

PAPERMODEL_OBJECT_PROPERTIES = [
    ("hasObjectiveFunction", "目标函数对象属性"),
    ("hasConstraintFunction", "约束函数对象属性"),
    ("usesParameter", "使用的参数变量对象属性"),
    ("hasMathematicalProblemType", "数学优化问题类型"),
    ("hasModeledTechnology", "模型覆盖的能源技术"),
    ("OEO_00000505", "模型覆盖的能源需求部门 / covers sector"),
]

def lookup_local_name_from_resource(resource):
    """Return local name for #Name or full OPF IRI."""
    if not resource:
        return ""
    value = str(resource)
    if value.startswith("#"):
        return value[1:]
    if value.startswith(OPF_IRI):
        return value[len(OPF_IRI):]
    if "#" in value and value.startswith(("http://", "https://")):
        return value.rsplit("#", 1)[-1]
    return value

def normalize_identity_text(value):
    """Normalize DOI/title text for matching."""
    value = str(value or "").lower()
    value = value.replace("https://doi.org/", "").replace("http://doi.org/", "")
    value = re.sub(r"doi:\s*", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())

def extract_title_doi_from_current_pdf():
    """Use existing 8.x extraction helpers if available; otherwise use current paper_model_record."""
    if "paper_model_record" in globals():
        metadata = paper_model_record.get("metadata", {})
        title = metadata.get("hasPaperTitle")
        doi = metadata.get("hasDOI")
        if title or doi:
            return title, doi

    if "PAPER_PATH" not in globals() or PAPER_PATH is None:
        raise RuntimeError("请先设置 PAPER_PATH，或先运行 8.5 生成 paper_model_record。")

    if "extract_paper_record" not in globals() or "extract_paper_metadata_with_llm" not in globals():
        raise RuntimeError("请先运行 8.1-8.5 的函数定义单元格，再运行 8.9.1。")

    paper_record_for_lookup = extract_paper_record(PAPER_PATH)
    paper_text = paper_record_for_lookup["llm_payload"]["prompt_text"]
    image_paths = paper_record_for_lookup["llm_payload"]["image_input_paths"]
    metadata = extract_paper_metadata_with_llm(paper_text, image_paths=image_paths)
    return metadata.get("hasPaperTitle"), metadata.get("hasDOI")

def is_opfmodel_element(individual_element):
    for child in individual_element:
        if child.tag.endswith("}type"):
            if lookup_local_name_from_resource(child.attrib.get(RDF_RESOURCE)) == "OPFModel":
                return True
    return False

def read_all_opfmodel_individuals_from_owl():
    xml_text = resolve_instance_owl_read_path().read_text(encoding="utf-8")
    root = ET.fromstring(xml_text)
    records = []
    for individual in root.iter():
        if not individual.tag.endswith("}NamedIndividual"):
            continue
        if not is_opfmodel_element(individual):
            continue
        data_properties = {}
        object_properties = {}
        for child in individual:
            tag = child.tag.split("}", 1)[-1]
            if tag == "type":
                continue
            resource = child.attrib.get(RDF_RESOURCE)
            if resource:
                object_properties.setdefault(tag, []).append(lookup_local_name_from_resource(resource))
            else:
                data_properties.setdefault(tag, []).append(child.text or "")
        records.append(
            {
                "iri": individual.attrib.get(RDF_ABOUT, ""),
                "local_name": lookup_local_name_from_resource(individual.attrib.get(RDF_ABOUT, "")),
                "data_properties": data_properties,
                "object_properties": object_properties,
            }
        )
    return records

def find_opfmodel_by_pdf_metadata(title, doi):
    title_norm = normalize_identity_text(title)
    doi_norm = normalize_identity_text(doi)
    candidates = read_all_opfmodel_individuals_from_owl()

    if doi_norm:
        doi_matches = [
            item for item in candidates
            if normalize_identity_text("; ".join(item["data_properties"].get("hasDOI", []))) == doi_norm
        ]
        if doi_matches:
            return doi_matches[0], "DOI exact match / DOI 精确匹配"

    if title_norm:
        title_matches = [
            item for item in candidates
            if normalize_identity_text("; ".join(item["data_properties"].get("hasPaperTitle", []))) == title_norm
        ]
        if title_matches:
            return title_matches[0], "paper title exact match / 论文标题精确匹配"

    return None, "not found / 未找到"

def value_needs_translation(value, translate_class_names=False):
    """Translate non-empty values; optionally translate ontology class names too."""
    text = str(value or "").strip()
    if not text:
        return False
    if text.lower() in {"true", "false", "none", "null"}:
        return False
    if re.fullmatch(r"\d{4}", text):
        return False
    if re.fullmatch(r"10\.\S+", text, flags=re.IGNORECASE):
        return False
    if re.search(r"[\u4e00-\u9fff]", text):
        return False
    if not translate_class_names and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text):
        return False
    return True

def translate_values_to_chinese(values, translate_class_names=False):
    """
    Translate printed values to Chinese in one LLM call.
    If the LLM route is unavailable, return an empty map and keep printing originals.
    """
    unique_values = []
    seen = set()
    for value in values:
        text = str(value or "").strip()
        if value_needs_translation(text, translate_class_names=translate_class_names) and text not in seen:
            seen.add(text)
            unique_values.append(text)
    if not unique_values:
        return {}

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "translations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "source": {"type": "string"},
                        "zh": {"type": "string"},
                    },
                    "required": ["source", "zh"],
                },
            }
        },
        "required": ["translations"],
    }
    system_prompt = render_prompt("paper_lookup.translation.system")
    user_prompt = render_prompt(
        "paper_lookup.translation.user",
        unique_values_json=json.dumps(unique_values, ensure_ascii=False, indent=2),
    )
    try:
        result = call_json_llm(system_prompt, user_prompt, "opfmodel_value_translation", schema, image_paths=None)
    except Exception as exc:
        print("中文翻译调用失败，下面只显示原文 / Chinese translation failed, originals only:", exc)
        return {}

    translations = {}
    for item in result.get("translations", []):
        source = str(item.get("source", "")).strip()
        zh = str(item.get("zh", "")).strip()
        if source and zh:
            translations[source] = zh
    return translations

def collect_data_values_for_translation(model_record):
    data_properties = model_record.get("data_properties", {})
    values = []
    for _, fields in PAPERMODEL_PRINT_SECTIONS:
        for property_name, _ in fields:
            values.extend(data_properties.get(property_name, []))
    return values

def collect_object_values_for_translation(model_record):
    object_properties = model_record.get("object_properties", {})
    values = []
    for property_name, _ in PAPERMODEL_OBJECT_PROPERTIES:
        values.extend(object_properties.get(property_name, []))
    return values

def print_property_values(label_en, label_zh, values, translations=None, translate_value=False, translate_class_names=False):
    print(f"{label_en} / {label_zh}")
    if not values:
        print("  None")
        return
    translations = translations or {}
    for value in values:
        value_text = str(value)
        print(f"  - {value_text}")
        if translate_value and value_needs_translation(value_text, translate_class_names=translate_class_names):
            zh = translations.get(value_text.strip())
            if zh:
                print(f"    {zh}")

def print_opfmodel_in_papermodel_format(model_record, match_reason=None, lookup_title=None, lookup_doi=None):
    print("\n" + "=" * 96)
    print("8.9.1 OPFModel 实例反查结果 / OPFModel Lookup Result")
    print("=" * 96)
    print("匹配方式 / Match reason:", match_reason or "None")
    print("PDF 论文标题 / PDF paper title:", lookup_title or "None")
    print("PDF DOI:", lookup_doi or "None")
    print("实例 IRI / Individual IRI:", model_record.get("iri"))
    print("实例名 / Local name:", model_record.get("local_name"))

    data_properties = model_record.get("data_properties", {})
    object_properties = model_record.get("object_properties", {})
    data_value_translations = translate_values_to_chinese(collect_data_values_for_translation(model_record))
    object_value_translations = translate_values_to_chinese(
        collect_object_values_for_translation(model_record),
        translate_class_names=True,
    )

    for section_title, fields in PAPERMODEL_PRINT_SECTIONS:
        print("\n## " + section_title)
        for property_name, zh_label in fields:
            print_property_values(
                property_name,
                zh_label,
                data_properties.get(property_name, []),
                translations=data_value_translations,
                translate_value=True,
            )

    print("\n## 5. ModelStructure ObjectProperties / 模型结构信息：对象属性")
    for property_name, zh_label in PAPERMODEL_OBJECT_PROPERTIES:
        print_property_values(
            property_name,
            zh_label,
            object_properties.get(property_name, []),
            translations=object_value_translations,
            translate_value=True,
            translate_class_names=True,
        )

    remaining_data = {
        key: value for key, value in data_properties.items()
        if key not in {field for _, fields in PAPERMODEL_PRINT_SECTIONS for field, _ in fields}
    }
    remaining_objects = {
        key: value for key, value in object_properties.items()
        if key not in {name for name, _ in PAPERMODEL_OBJECT_PROPERTIES}
    }
    if remaining_data:
        print("\n## 6. Other DataProperties / 其他数据属性")
        print(json.dumps(remaining_data, ensure_ascii=False, indent=2))
    if remaining_objects:
        print("\n## 7. Other ObjectProperties / 其他对象属性")
        print(json.dumps(remaining_objects, ensure_ascii=False, indent=2))

    print("=" * 96 + "\n")
    return model_record
