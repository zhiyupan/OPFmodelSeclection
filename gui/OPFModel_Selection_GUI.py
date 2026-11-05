from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.opfmodelselection.config import (  # noqa: E402
    INSTANCE_OWL_PATH,
    PAPER_DIR,
    RECOMMENDATION_HUMAN_GOLD_CSV,
)
from src.opfmodelselection.online_lookup import (  # noqa: E402
    extract_pdf_title_and_doi,
    find_paper_model_by_pdf_metadata,
)
from src.opfmodelselection.online_recommendation import (  # noqa: E402
    read_all_paper_model_instances,
    run_direct_online_recommendation_pipeline,
)
from src.opfmodelselection.paper_extraction import (  # noqa: E402
    extract_paper_model_record,
    review_and_prune_paper_model_record,
)
from src.opfmodelselection.paper_writer import (  # noqa: E402
    delete_paper_model_instances_from_ontology,
    write_single_paper_model_instance_to_ontology,
)
from src.opfmodelselection.validation2 import (  # noqa: E402
    VALIDATION2_ACCURACY_BY_REQUIREMENT_CSV,
    VALIDATION2_ACCURACY_SUMMARY_CSV,
    VALIDATION2_TOP3_CSV,
    evaluate_validation2_accuracy,
)
from src.opfmodelselection.user_requirements import (  # noqa: E402
    USER_REQUIREMENTS,
    USER_REQUIREMENTS_BY_ID,
)
from src.opfmodelselection.semantic_evaluation import (  # noqa: E402
    PAPER_INGESTION_FACTUAL_ACCURACY_DETAILS_CSV,
    PAPER_INGESTION_SEMANTIC_SIMILARITY_DETAILS_CSV,
    PAPER_INGESTION_QUALITY_VALIDATION_DIR,
    PAPER_INGESTION_VALIDATION_SUMMARY_CSV,
)
from src.opfmodelselection import semantic_evaluation as semantic_evaluation_module  # noqa: E402


TEXT = {
    "en": {
        "title": "OPF Model Knowledge Graph GUI",
        "caption": "Paper ingestion writes to OPF_Knowledge_Graph2.0.owl. Online recommendation reads from the same knowledge graph.",
        "paper": "Paper ingestion",
        "recommend": "Online recommendation",
        "validation": "Validation",
        "validation2": "Validation2.0",
        "language": "Language",
        "page": "Page",
        "upload": "Upload a PDF paper",
        "extract": "Extract and review",
        "write": "Confirm and write to knowledge graph",
        "rerun": "Run extraction again",
        "delete_existing": "Delete matched existing PaperModel",
        "existing": "Existing PaperModel check",
        "requirement": "User requirement",
        "run_recommend": "Run recommendation",
        "top3": "Top-3 recommended models",
        "intermediate": "Intermediate results",
        "validation_run": "Recalculate Validation2.0 metrics",
        "validation_saved": "Saved Validation2.0 tables",
        "metric": "Metric",
        "meaning": "Meaning",
    },
    "zh": {
        "title": "OPF 模型知识图谱前端",
        "caption": "论文写入页面写入 OPF_Knowledge_Graph2.0.owl，在线推荐页面从同一知识图谱读取模型。",
        "paper": "论文写入知识图谱",
        "recommend": "在线用户需求推荐",
        "validation": "验证评估",
        "validation2": "Validation2.0",
        "language": "界面语言",
        "page": "功能页面",
        "upload": "上传 PDF 论文",
        "extract": "提取并复核",
        "write": "确认无误并写入知识图谱",
        "rerun": "重新提取",
        "delete_existing": "删除匹配到的已入库 PaperModel",
        "existing": "已入库 PaperModel 检查",
        "requirement": "用户自然语言需求",
        "run_recommend": "开始推荐",
        "top3": "最终推荐模型 Top-3",
        "intermediate": "中间结果",
        "validation_run": "重新计算 Validation2.0 指标",
        "validation_saved": "已保存的 Validation2.0 表格",
        "metric": "指标",
        "meaning": "含义",
    },
}

METRIC_TRANSLATIONS = {
    "Enterprise Requirements Candidate Top-3 Accuracy": {
        "zh": "企业需求候选集合 Top-3 命中率",
        "meaning_zh": "企业需求中，推荐 Top-3 有多少属于人工可接受候选集合的平均比例。",
    },
    "Motivation nDCG@3": {
        "zh": "Motivation 需求 nDCG@3",
        "meaning_zh": "Motivation 需求中，系统 Top-3 排序与人工有序 ranking 的一致程度。nDCG@3 越高，排序越接近人工标准答案。",
    },
}

COLUMN_TRANSLATIONS = {
    "Requirement ID": "需求编号",
    "Requirement count": "需求数量",
    "Requirement type": "需求类型",
    "Requirement group": "需求分组",
    "Requirement name": "需求名称",
    "Requirement text": "需求文本",
    "Predicted Top3": "系统推荐 Top3",
    "Gold answer": "人工标准答案",
    "Gold acceptable instance": "人工可接受实例",
    "Gold rank": "人工排序",
    "Gold instance": "人工排序实例",
    "Relevance": "相关性权重",
    "Metric": "指标",
    "Hit count": "命中数量",
    "DCG": "DCG",
    "IDCG": "IDCG",
    "Score": "得分",
    "Score (%)": "得分（%）",
    "Average score": "平均得分",
    "Average score (%)": "平均得分（%）",
    "Meaning": "含义",
    "Explanation": "解释",
    "Top rank": "推荐排序",
    "Instance": "实例",
    "Model name": "模型名",
    "PDF file": "PDF 文件",
    "Paper title": "论文标题",
    "Final score": "最终分",
    "Recommendation reason": "推荐理由",
    "Matched needs": "匹配点",
    "Strengths": "优点",
    "Limitations": "不足",
    "Simple explanation": "模型简述",
    "Objective text": "目标函数文本",
    "Constraint text": "约束文本",
    "Parameter text": "参数变量文本",
    "Mathematical problem types": "数学问题类型",
    "Technologies": "建模技术",
    "Sectors": "覆盖部门",
}

VALUE_TRANSLATIONS = {
    "English": "英文",
    "Basic": "基础",
    "Data property": "数据属性",
    "Object property": "对象属性",
    "Enterprise candidate set": "企业需求候选集合",
    "Motivation ordered ranking": "Motivation 需求有序 ranking",
    "Enterprise Requirements": "企业需求",
    "Motivation Requirements": "Motivation 需求",
    "nDCG@3 with gold relevance: rank1=4, rank2=0.5, rank3=0.5.": "使用人工相关性权重计算 nDCG@3：人工第 1 名 = 4，第 2 名 = 0.5，第 3 名 = 0.5。",
    "Top3 hit rate against the human acceptable candidate set.": "系统 Top3 与人工可接受候选集合的命中率。",
    "Top3 hit count divided by 3.": "Top3 命中数量除以 3。",
    "Cost-efficient Operation": "成本效率型运行需求",
    "Security-Constrained Operation": "安全约束运行需求",
    "Renewable Uncertainty Handling": "新能源不确定性处理需求",
    "Real-Time Feasibility": "实时可行性需求",
    "Environmental / Sustainability Requirement": "低碳与可持续需求",
    "Concentrated Load / Data Center Integration": "集中负荷与数据中心接入需求",
    "Peak Load Management / Peak Shaving": "峰值负荷管理需求",
    "Reliability Improvement": "供电可靠性提升需求",
    "Resource Adequacy / Supply Sufficiency": "资源充裕与供应充足需求",
    "Multi-Area / Cross-Border Coordination": "多区域 / 跨区协调需求",
    "Dynamic Stability / Inverter-Dominated Grid Security": "动态稳定与变流器主导系统安全需求",
    "Energy Storage Scheduling": "储能调度需求",
    "Market-Oriented Operation": "市场化运行需求",
    "Data Privacy / Decentralized Coordination": "数据隐私与分布式协调需求",
    "Computational Speed / Online Tractability and Accuracy and Physical Feasibility": "快速求解、在线可部署、精确性与物理可行性需求",
    "Unit Commitment Coupled Operation": "机组启停联合调度需求",
    "Line Congestion and Thermal Limit Management": "线路拥塞与热限额管理需求",
    "Local Flexibility Service Delivery": "本地灵活性服务交付与验证需求",
    "Scalability to Large Power Systems": "大规模系统可扩展性需求",
    "Real-time frequency-constrained OPF": "实时频率约束 OPF",
    "Fast preventive SCOPF for volatile renewables": "面向新能源波动的快速预防型 SCOPF",
    "Large-scale meshed SOCP AC-OPF": "大规模网状网络 SOCP AC-OPF",
    "Stochastic UC-OPF microgrid EMS": "随机 UC-OPF 微电网 EMS",
    "Distributed confidential CC-OPF": "分布式保密机会约束 OPF",
    "Data-driven AC-OPF with topology labels": "带拓扑标签的数据驱动 AC-OPF",
    "Physics-informed ACOPF with calibration": "带可行性校正的物理信息 ACOPF",
    "Physics-informed data-driven OPF replacement": "替代迭代 OPF 的物理信息数据驱动模型",
    "Best-fit participation factor DA/RT OPF": "基于最佳参与因子的日前 / 实时 OPF",
    "Distributed MTDC OPF-for-ANM": "面向主动网络管理的分布式 MTDC OPF",
    "Discrete LTC DOPF": "含离散 LTC 的配电网 DOPF",
    "Distributed OPF with unreliable communication": "通信不可靠条件下的分布式 OPF",
    "Feeder reconfiguration SOCP relaxation": "馈线重构 SOCP 松弛模型",
    "Grid Foundation Model for power systems": "电力系统基础模型 GridFM",
    "Economic low-carbon stochastic RES OPF": "经济低碳随机新能源 OPF",
    "Hybrid UC and OPF correction for PV": "PV 接入下 UC 与 OPF 校正混合模型",
    "D-OPF benchmarking framework": "D-OPF 基准评估框架",
    "Wind farm primary voltage control OPF": "风电场一次电压控制 OPF",
    "ML-aided fast SCOPF": "机器学习辅助快速 SCOPF",
    "Multi-period hybrid AC/DC OPF flexibility market": "多周期混合 AC/DC-OPF 灵活性市场模型",
    "Dynamic security-constrained AC-OPF with neural encoding": "神经网络编码动态安全约束 AC-OPF",
    "Scalable N-k SCOPF with adversarial robustness": "具备对抗鲁棒性的可扩展 N-k SCOPF",
    "Online optimization for high-renewable grids": "高比例新能源电网在线优化",
    "Hybrid AC/DC OPF with VSC-MTDC and renewables": "含 VSC-MTDC 与新能源的混合 AC/DC OPF",
    "Local scalable GNN-based ACOPF approximation": "局部可扩展 GNN ACOPF 近似模型",
    "Physics-informed neural network framework": "物理信息神经网络框架",
    "Fast physically constrained data-driven AC-OPF": "快速物理约束数据驱动 AC-OPF",
    "Probabilistically robust AC-OPF under uncertainty": "不确定性下的概率鲁棒 AC-OPF",
    "Real-time OPF with Lagrangian reinforcement learning": "基于拉格朗日强化学习的实时 OPF",
    "Real-time sequential SCOPF decision model": "实时序贯 SCOPF 决策模型",
    "Reserve-constrained AC-OPF with energy and reserve co-optimization": "能量与备用联合优化的备用约束 AC-OPF",
    "Large-scale multi-period SCOPF": "大规模多时段 SCOPF",
    "Multi-period OPF for community storage and PV sizing": "社区储能与 PV 容量配置多时段 OPF",
    "Unbalanced three-phase OPF for smart distribution grids": "智能配电网三相不平衡 OPF",
    "DR-based AC-OPF with flexible-load aggregators and uncertainty": "含柔性负荷聚合器与不确定性的需求响应 AC-OPF",
}


TEXT["zh"].update(
    {
        "title": "OPF 模型知识图谱前端",
        "caption": "论文写入页面写入 OPF_Knowledge_Graph2.0.owl，在线推荐页面从同一知识图谱读取模型。",
        "paper": "论文写入知识图谱",
        "recommend": "在线用户需求推荐",
        "validation": "验证评估",
        "validation2": "Validation2.0",
        "language": "界面语言",
        "page": "功能页面",
        "upload": "上传 PDF 论文",
        "extract": "提取并复核",
        "write": "确认无误并写入知识图谱",
        "rerun": "重新提取",
        "delete_existing": "删除匹配到的已入库 PaperModel",
        "existing": "已入库 PaperModel 检查",
        "requirement": "用户自然语言需求",
        "run_recommend": "开始推荐",
        "top3": "最终推荐模型 Top-3",
        "intermediate": "中间结果",
        "validation_run": "重新计算 Validation2.0 指标",
        "validation_saved": "已保存的 Validation2.0 表格",
        "metric": "指标",
        "meaning": "含义",
    }
)


def current_language_mode() -> str:
    return st.session_state.get("language_mode", "bilingual")


def bilingual_text(en_text: str, zh_text: str) -> str:
    return text_for_mode(en_text, zh_text, current_language_mode())


def text_for_mode(en_text: str, zh_text: str, mode: str) -> str:
    if mode == "en":
        return en_text
    if mode == "zh":
        return zh_text
    return f"{en_text} / {zh_text}"


def tr(key: str) -> str:
    en_text = TEXT["en"].get(key, key)
    zh_text = TEXT["zh"].get(key, en_text)
    return text_for_mode(en_text, zh_text, current_language_mode())


_HAN_CHARACTER_RE = re.compile(r"[\u3400-\u9fff]")
_ENGLISH_WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
_BILINGUAL_UNIT_RESTART_RE = re.compile(
    r"；|(?<=[.!?])\s+(?=[\u3400-\u9fff])"
)
_LIST_ITEM_PREFIX_RE = re.compile(r"^(\s*(?:[-*•]|\d+[.)])\s+)")

_BILINGUAL_RESULT_TEXT_COLUMNS = {
    "why matched",
    "why_matched",
    "risk or gap",
    "main_risk_or_gap",
    "recommendation reason",
    "recommendation_reason",
    "matched needs",
    "matched_needs",
    "strengths",
    "limitations",
    "simple explanation",
    "simple_model_explanation",
    "supporting evidence",
    "supporting_evidence",
    "overall summary",
    "overall_summary",
    "factual judgment reason",
    "factual_judgment_reason",
}


def _contains_han(text: str) -> bool:
    return bool(_HAN_CHARACTER_RE.search(text))


def _has_substantive_english(text: str) -> bool:
    words = _ENGLISH_WORD_RE.findall(text)
    latin_letter_count = sum(char.isascii() and char.isalpha() for char in text)
    return len(words) >= 2 or latin_letter_count >= 8


def _bilingual_pair_from_unit(text: str) -> tuple[str, str] | None:
    """Return an English/Chinese pair only for a high-confidence language boundary."""
    unit = text.strip()
    if not unit or not _contains_han(unit):
        return None

    candidates = []
    for index, char in enumerate(unit):
        if char != "/":
            continue
        if (index and unit[index - 1] == "/") or (
            index + 1 < len(unit) and unit[index + 1] == "/"
        ):
            continue

        previous = unit[index - 1] if index else ""
        following = unit[index + 1] if index + 1 < len(unit) else ""
        compact_ascii_slash = (
            previous
            and following
            and not previous.isspace()
            and not following.isspace()
            and previous.isascii()
            and previous.isalnum()
            and following.isascii()
            and following.isalnum()
        )
        if compact_ascii_slash:
            continue

        left = unit[:index].strip()
        right = unit[index + 1 :].strip()
        left_han_count = len(_HAN_CHARACTER_RE.findall(left))
        right_han_count = len(_HAN_CHARACTER_RE.findall(right))

        if left_han_count >= 2 and right_han_count == 0 and _has_substantive_english(right):
            candidates.append((len(right), right, left))
        elif right_han_count >= 2 and left_han_count == 0 and _has_substantive_english(left):
            candidates.append((len(left), left, right))

    if not candidates:
        return None
    _, english_text, chinese_text = max(candidates, key=lambda item: item[0])
    return english_text.strip(), chinese_text.strip()


def _identical_slash_sides(text: str) -> str | None:
    parts = re.split(r"\s+/\s+", text.strip())
    if len(parts) == 2 and parts[0].strip() == parts[1].strip():
        return parts[0].strip()
    return None


def _localize_bilingual_line(text: str, mode: str) -> str:
    prefix_match = _LIST_ITEM_PREFIX_RE.match(text)
    prefix = prefix_match.group(1) if prefix_match else ""
    content = text[len(prefix) :]
    chunks = [chunk for chunk in _BILINGUAL_UNIT_RESTART_RE.split(content) if chunk]

    identical_value = _identical_slash_sides(content)
    if identical_value is not None:
        return prefix + identical_value

    whole_pair = _bilingual_pair_from_unit(content)
    later_chunk_has_pair = any(
        _bilingual_pair_from_unit(chunk) is not None for chunk in chunks[1:]
    )
    if whole_pair and not later_chunk_has_pair:
        return prefix + whole_pair[0 if mode == "en" else 1]

    if len(chunks) == 1:
        return text

    localized_units = []
    pending_chunks = []
    for chunk in chunks:
        pending_chunks.append(chunk)
        pending_text = "；".join(pending_chunks)
        identical_value = _identical_slash_sides(pending_text)
        if identical_value is not None:
            localized_units.append(identical_value)
            pending_chunks = []
            continue
        pair = _bilingual_pair_from_unit(pending_text)
        if pair:
            localized_units.append(pair[0 if mode == "en" else 1])
            pending_chunks = []

    if pending_chunks:
        pending_text = "；".join(pending_chunks)
        identical_value = _identical_slash_sides(pending_text)
        if identical_value is not None:
            localized_units.append(identical_value)
        else:
            pair = _bilingual_pair_from_unit(pending_text)
            localized_units.append(
                pair[0 if mode == "en" else 1] if pair else pending_text
            )

    separator = "; " if mode == "en" else "；"
    localized = separator.join(
        unit.strip() for unit in localized_units if unit.strip()
    )
    if mode == "en":
        localized = re.sub(r"([.!?])\s*;\s+", r"\1 ", localized)
    else:
        localized = re.sub(r"([。！？])；", r"\1 ", localized)
    return prefix + localized


def localize_bilingual_result_text(value, mode: str | None = None):
    """Localize a bilingual LLM result for display without changing stored data."""
    selected_mode = mode or current_language_mode()
    if selected_mode == "bilingual":
        return value
    if isinstance(value, list):
        return [localize_bilingual_result_text(item, selected_mode) for item in value]
    if isinstance(value, tuple):
        return tuple(localize_bilingual_result_text(item, selected_mode) for item in value)
    if isinstance(value, dict):
        return {
            key: localize_bilingual_result_text(item, selected_mode)
            for key, item in value.items()
        }
    if not isinstance(value, str):
        return value

    localized = "\n".join(
        _localize_bilingual_line(line, selected_mode)
        for line in value.split("\n")
    )
    if selected_mode == "en" and _contains_han(localized):
        return "English explanation unavailable for this result."
    return localized


def _column_contains_bilingual_result_text(column: str) -> bool:
    english_column = column.split(" / ", 1)[0].strip().casefold()
    return english_column in _BILINGUAL_RESULT_TEXT_COLUMNS


def _clear_recommendation_state() -> None:
    """Discard result state that belongs to a previous requirement."""
    for key in (
        "recommendation_result",
        "recommendation_result_requirement_text",
        "selected_execution_model",
    ):
        st.session_state.pop(key, None)


def _load_selected_canonical_requirement() -> None:
    requirement_id = st.session_state.get("canonical_requirement_id", "")
    requirement = USER_REQUIREMENTS_BY_ID.get(requirement_id)
    if requirement:
        st.session_state["requirement_text"] = requirement["requirement_text"]
    _clear_recommendation_state()


def _handle_requirement_text_change() -> None:
    """Keep the selector, editable text, and displayed result synchronized."""
    requirement_id = st.session_state.get("canonical_requirement_id", "")
    canonical = USER_REQUIREMENTS_BY_ID.get(requirement_id)
    current_text = st.session_state.get("requirement_text", "")
    if canonical and current_text != canonical["requirement_text"]:
        # Once a canonical example is edited it becomes a custom requirement.
        st.session_state["canonical_requirement_id"] = ""
    _clear_recommendation_state()


def translate_value(value):
    if not isinstance(value, str):
        return value
    zh_value = VALUE_TRANSLATIONS.get(value)
    if not zh_value:
        return value
    mode = current_language_mode()
    if mode == "zh":
        return zh_value
    if mode == "bilingual":
        return f"{value} / {zh_value}"
    return value


def translate_column(column: str) -> str:
    if " / " in column:
        en_column, zh_column = column.split(" / ", 1)
        if any("\u4e00" <= char <= "\u9fff" for char in zh_column):
            mode = current_language_mode()
            if mode == "zh":
                return zh_column
            if mode == "bilingual":
                return f"{en_column} / {zh_column}"
            return en_column
    zh_column = COLUMN_TRANSLATIONS.get(column)
    if not zh_column:
        return column
    mode = current_language_mode()
    if mode == "zh":
        return zh_column
    if mode == "bilingual":
        return f"{column} / {zh_column}"
    return column


def localize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    display = df.copy()
    for column in display.columns:
        if display[column].dtype == object:
            display[column] = display[column].map(translate_value)
            if _column_contains_bilingual_result_text(str(column)):
                display[column] = display[column].map(localize_bilingual_result_text)
    display = display.rename(columns={column: translate_column(str(column)) for column in display.columns})
    display.index = range(1, len(display) + 1)
    return display


def safe_dataframe(df: pd.DataFrame, height: int | None = None, localize: bool = True):
    display = localize_dataframe(df) if localize else df.copy()
    display.index = range(1, len(display) + 1)
    kwargs = {"width": "stretch"}
    if height is not None:
        kwargs["height"] = height
    st.dataframe(display, **kwargs)


def save_uploaded_pdf(uploaded_file) -> Path:
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    target = PAPER_DIR / uploaded_file.name
    target.write_bytes(uploaded_file.getbuffer())
    return target


def record_to_preview_rows(record: dict) -> pd.DataFrame:
    rows = []
    for section_name in ["metadata", "structure", "features"]:
        section = record.get(section_name, {})
        if not isinstance(section, dict):
            continue
        for key, value in section.items():
            if value is None:
                display_value = ""
            elif isinstance(value, (list, dict)):
                display_value = json.dumps(value, ensure_ascii=False)
            else:
                display_value = str(value)
            rows.append(
                {
                    "section / 部分": section_name,
                    "field / 字段": key,
                    "value / 内容": display_value,
                }
            )
    return pd.DataFrame(rows)


def render_existing_pdf_check(pdf_path: Path):
    st.subheader(tr("existing"))
    try:
        pdf_info = extract_pdf_title_and_doi(pdf_path)
        matches = find_paper_model_by_pdf_metadata(pdf_info)
    except Exception as exc:
        st.error(f"{bilingual_text('Existing check failed', '已入库检查失败')}: {exc}")
        return
    st.json(pdf_info)
    if not matches:
        st.info(bilingual_text("No matched PaperModel was found.", "未找到匹配的已入库 PaperModel。"))
        return
    rows = []
    for match in matches:
        record = match.get("model", {})
        props = record.get("data_properties", {})
        rows.append(
            {
                "instance / 实例": record.get("instance_name", ""),
                "match reason / 匹配原因": match.get("match_type", ""),
                "title similarity / 标题相似度": match.get("score", ""),
                "paper title / 论文标题": props.get("hasPaperTitle", ""),
                "doi / DOI": props.get("hasDOI", ""),
            }
        )
    safe_dataframe(pd.DataFrame(rows))
    selected = st.multiselect(
        tr("delete_existing"),
        [row["instance / 实例"] for row in rows if row["instance / 实例"]],
    )
    if selected and st.button(tr("delete_existing"), type="secondary", width="stretch"):
        result = delete_paper_model_instances_from_ontology(selected, save=True)
        st.success(str(result))


def render_paper_page():
    st.header(tr("paper"))
    uploaded = st.file_uploader(tr("upload"), type=["pdf"])
    if not uploaded:
        st.info(bilingual_text("Upload a local PDF to start.", "上传本地 PDF 后开始。"))
        return

    pdf_path = save_uploaded_pdf(uploaded)
    st.success(f"{bilingual_text('Saved PDF', '已保存 PDF')}: {pdf_path}")
    render_existing_pdf_check(pdf_path)

    col1, col2 = st.columns(2)
    with col1:
        extract_clicked = st.button(tr("extract"), type="primary", width="stretch")
    with col2:
        if st.button(tr("rerun"), width="stretch"):
            st.session_state.pop("paper_model_record", None)
            st.rerun()

    if extract_clicked:
        with st.spinner(bilingual_text("Extracting and reviewing paper model...", "正在提取并复核论文模型...")):
            record = extract_paper_model_record(pdf_path)
            reviewed = review_and_prune_paper_model_record(record)
            st.session_state["paper_model_record"] = reviewed

    record = st.session_state.get("paper_model_record")
    if not record:
        return

    st.subheader(bilingual_text("Reviewed preview before writing", "写入前复核预览"))
    safe_dataframe(record_to_preview_rows(record), height=420)
    st.download_button(
        bilingual_text("Download reviewed JSON", "下载复核 JSON"),
        data=json.dumps(record, ensure_ascii=False, indent=2),
        file_name="paper_model_record_reviewed.json",
        mime="application/json",
        key="download_reviewed_json",
    )

    confirm = st.checkbox(bilingual_text("I have checked the preview and confirm it is correct.", "我已检查预览并确认无误。"))
    if confirm and st.button(tr("write"), type="primary", width="stretch"):
        with st.spinner(bilingual_text("Writing to knowledge graph...", "正在写入知识图谱...")):
            written = write_single_paper_model_instance_to_ontology(record, append=True, save=True)
        st.success(bilingual_text("Written and saved.", "已写入并保存。"))
        st.json(written if isinstance(written, dict) else {"result": str(written)})


def flatten_prefilter(result: dict) -> pd.DataFrame:
    return flatten_prefilter_candidates(result)


def prefilter_candidate_items(result: dict) -> list:
    current_items = result.get("prefilter_candidates", []) or []
    if current_items:
        return current_items

    # Compatibility for recommendation results produced before the direct
    # prefilter-to-close-reading pipeline was introduced.
    selected = (result.get("prefilter_result", {}) or {}).get("selected_candidates", []) or []
    if not selected:
        return []

    kg_by_name = {}
    for item in result.get("top15_candidates", []) or []:
        kg_info = item.get("kg_info", {})
        name = kg_info.get("instance_name", "")
        if name:
            kg_by_name[name] = kg_info
    try:
        for kg_info in read_all_paper_model_instances(INSTANCE_OWL_PATH):
            name = kg_info.get("instance_name", "")
            if name:
                kg_by_name.setdefault(name, kg_info)
    except Exception:
        pass

    return [
        {
            "evidence_package": item,
            "kg_info": kg_by_name.get(
                item.get("instance_name", ""),
                {"instance_name": item.get("instance_name", "")},
            ),
        }
        for item in selected
    ]


def flatten_prefilter_candidates(result: dict) -> pd.DataFrame:
    rows = []
    for idx, item in enumerate(prefilter_candidate_items(result), start=1):
        kg_info = item.get("kg_info", {})
        props = kg_info.get("data_properties", {})
        evidence = item.get("evidence_package", {})
        rows.append(
            {
                "Rank / 排序": idx,
                "PDF file / PDF 文件": props.get("hasSourceFileName", ""),
                "Model / 模型": props.get("hasModelName", "") or kg_info.get("instance_name", ""),
                "Prefilter score / 初筛分": evidence.get("prefilter_score", ""),
                "Why matched / 匹配原因": evidence.get("why_matched", ""),
                "Risk or gap / 限制或风险": evidence.get("main_risk_or_gap", ""),
            }
        )
    return pd.DataFrame(rows)


def flatten_close_reading(result: dict) -> pd.DataFrame:
    rows = []
    close_reading = result.get("close_reading_result", {})
    ranked = close_reading.get("ranked_candidates", [])
    if not ranked:
        ranked = (result.get("rerank_result", {}) or {}).get("ranked_candidates", [])
    for idx, item in enumerate(ranked, start=1):
        rows.append(
            {
                "Rank / 排序": item.get("rank", idx),
                "Model / 模型": item.get("instance_name", ""),
                "Final score / 最终分": item.get("final_score", ""),
                "Recommendation reason / 推荐理由": item.get("recommendation_reason", ""),
                "Matched needs / 匹配点": item.get("matched_needs", ""),
                "Strengths / 优点": item.get("strengths", ""),
                "Limitations / 不足": item.get("limitations", ""),
            }
        )
    return pd.DataFrame(rows)


def candidate_lookup_by_instance(result: dict) -> dict:
    lookup = {}
    for candidate in prefilter_candidate_items(result):
        kg_info = candidate.get("kg_info", {})
        name = kg_info.get("instance_name")
        if name:
            lookup[name] = candidate
    return lookup


def is_legacy_recommendation_result(result: dict) -> bool:
    return bool(
        result.get("consistency_result")
        or result.get("raw_consistency")
        or result.get("rerank_result")
        or result.get("raw_rerank")
    )


def kg_info_to_dataframe(kg_info: dict) -> pd.DataFrame:
    rows = []
    rows.append(
        {
            "Section / 部分": "Basic",
            "Property / 属性": "instance_name",
            "Value / 值": kg_info.get("instance_name", ""),
        }
    )
    for section_key, section_label in [
        ("data_properties", "Data property"),
        ("object_properties", "Object property"),
    ]:
        section = kg_info.get(section_key, {})
        if not isinstance(section, dict):
            continue
        for prop, value in section.items():
            if isinstance(value, (dict, list)):
                value_text = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_text = str(value)
            rows.append(
                {
                    "Section / 部分": section_label,
                    "Property / 属性": prop,
                    "Value / 值": value_text,
                }
            )
    return pd.DataFrame(rows)


def render_top3_model_card(row: dict, kg_info: dict | None = None) -> None:
    title = row.get("instance_name", "")
    with st.container(border=True):
        st.markdown(f"### Top {row.get('rank', '')}: {title}")
        st.metric(bilingual_text("Final score", "最终分"), row.get("final_score", ""))

        tab_reading, tab_kg, tab_execute = st.tabs(
            [
                bilingual_text("Close-reading content", "精读内容"),
                bilingual_text("Ontology instance", "本体实例查看"),
                bilingual_text("Execute", "执行"),
            ]
        )
        with tab_reading:
            for key, label_en, label_zh in [
                ("recommendation_reason", "Recommendation reason", "推荐理由"),
                ("matched_needs", "Matched needs", "匹配点"),
                ("strengths", "Strengths", "优点"),
                ("limitations", "Limitations", "不足"),
                ("simple_model_explanation", "Simple explanation", "模型简述"),
            ]:
                st.write(f"**{bilingual_text(label_en, label_zh)}**")
                st.write(localize_bilingual_result_text(row.get(key, "")))

        with tab_kg:
            if kg_info:
                safe_dataframe(kg_info_to_dataframe(kg_info), height=420)
            else:
                st.info(bilingual_text(
                    "No ontology-instance detail is available in the current recommendation result.",
                    "当前推荐结果中没有可展示的本体实例详情。",
                ))

        with tab_execute:
            st.info(bilingual_text(
                "Execution is a placeholder for connecting this selected PaperModel to a solver, notebook, or external implementation. The current GUI records the selected model and its ontology details for the next execution step.",
                "执行功能是预留入口，用于将所选 PaperModel 连接到求解器、Notebook 或外部实现。当前 GUI 会展示并保留该模型及其本体详情，供下一步执行接入使用。",
            ))
            if st.button(
                bilingual_text("Select this model for execution", "选择该模型用于执行"),
                key=f"execute_{row.get('rank', '')}_{title}",
                width="stretch",
            ):
                st.session_state["selected_execution_model"] = {
                    "requirement_id": st.session_state.get(
                        "canonical_requirement_id", ""
                    ),
                    "requirement_text": st.session_state.get(
                        "recommendation_result_requirement_text", ""
                    ),
                    "recommendation": row,
                    "kg_info": kg_info or {},
                }
                st.success(bilingual_text(
                    "This model has been selected for execution preparation.",
                    "已选择该模型用于执行准备。",
                ))


def render_recommendation_intermediate(result: dict) -> None:
    with st.expander(tr("intermediate"), expanded=True):
        diagnostics = pd.DataFrame(result.get("llm_input_diagnostics", []))
        if not diagnostics.empty:
            st.markdown(f"#### {bilingual_text('LLM input length check', 'LLM 输入输出长度检测')}")
            st.caption(bilingual_text(
                "This table records the estimated input size for each LLM call in this recommendation run.",
                "该表记录本次推荐流程中每次 LLM 调用的输入规模估算。",
            ))
            safe_dataframe(diagnostics, height=220)

        prefilter_df = flatten_prefilter(result)
        if not prefilter_df.empty:
            st.markdown(f"#### {bilingual_text('Prefilter candidates', '初筛候选模型')}")
            st.caption(bilingual_text(
                "These are all merged candidates with a prefilter score of at least 65. Every model in this table proceeds to complete close reading.",
                "这些是分组初筛合并后达到 65 分的全部候选模型。表中的每个模型都会进入完整精读。",
            ))
            safe_dataframe(prefilter_df, height=320)
        else:
            st.info(bilingual_text(
                "No prefilter candidate is available in the current result.",
                "当前结果中没有可展示的初筛候选模型。",
            ))

        close_reading_df = flatten_close_reading(result)
        if not close_reading_df.empty:
            st.markdown(f"#### {bilingual_text('Complete close-reading results', '完整精读结果')}")
            st.caption(bilingual_text(
                "Every prefilter candidate is independently reviewed and scored here. The final Top-3 is selected only after the program confirms that no candidate was omitted.",
                "这里会对每个初筛候选进行独立精读和评分。程序确认没有候选被遗漏后，才截取最终 Top-3。",
            ))
            safe_dataframe(close_reading_df, height=340)


def render_recommendation_page():
    st.header(tr("recommend"))
    try:
        model_count = len(read_all_paper_model_instances(INSTANCE_OWL_PATH))
        st.info(f"{bilingual_text('Loaded PaperModel instances', '已加载 PaperModel 实例')}: {model_count}")
    except Exception as exc:
        st.error(f"{bilingual_text('Could not read knowledge graph', '无法读取知识图谱')}: {exc}")

    if "canonical_requirement_id" not in st.session_state:
        st.session_state["canonical_requirement_id"] = "R02"
    if "requirement_text" not in st.session_state:
        st.session_state["requirement_text"] = USER_REQUIREMENTS_BY_ID["R02"][
            "requirement_text"
        ]
    st.selectbox(
        bilingual_text(
            "Canonical requirement example (optional)",
            "权威需求示例（可选）",
        ),
        options=[""] + [item["requirement_id"] for item in USER_REQUIREMENTS],
        format_func=lambda requirement_id: (
            bilingual_text("Custom natural-language input", "自定义自然语言输入")
            if not requirement_id
            else (
                f"{requirement_id} · "
                f"{USER_REQUIREMENTS_BY_ID[requirement_id]['requirement_name']}"
            )
        ),
        key="canonical_requirement_id",
        on_change=_load_selected_canonical_requirement,
    )
    st.caption(bilingual_text(
        "The 54 examples above and batch validation use the same canonical CSV. "
        "After loading one, the natural-language text remains editable.",
        "上面的 54 条示例与批量 Validation 读取同一份权威 CSV；载入后仍可编辑自然语言文本。",
    ))
    requirement = st.text_area(
        tr("requirement"),
        key="requirement_text",
        height=160,
        on_change=_handle_requirement_text_change,
    )

    running = st.session_state.get("recommendation_running", False)
    if st.button(tr("run_recommend"), type="primary", width="stretch", disabled=running):
        st.session_state["recommendation_running"] = True
        _clear_recommendation_state()
        try:
            with st.spinner(bilingual_text("Running recommendation...", "正在运行推荐...")):
                result = run_direct_online_recommendation_pipeline(requirement)
                st.session_state["recommendation_result"] = result
                st.session_state["recommendation_result_requirement_text"] = requirement
        finally:
            st.session_state["recommendation_running"] = False
        st.rerun()

    result = st.session_state.get("recommendation_result")
    result_requirement_text = st.session_state.get(
        "recommendation_result_requirement_text"
    )
    if result and result_requirement_text != requirement:
        # This guard also handles stale state created by an older GUI version
        # or a widget callback that did not fire as expected.
        _clear_recommendation_state()
        result = None
    if not result:
        # An execution selection is meaningful only while its bound
        # recommendation result is still present.
        st.session_state.pop("recommendation_result_requirement_text", None)
        st.session_state.pop("selected_execution_model", None)
        return

    if is_legacy_recommendation_result(result):
        st.warning(bilingual_text(
            "This is a cached result from the former consistency-check workflow. Its intermediate data is shown below using compatibility mode. Run the recommendation again to obtain a result from the current direct prefilter-to-close-reading pipeline.",
            "这是旧版“一致性检查”流程缓存下来的结果。下面会通过兼容模式展示其中间数据；请重新点击“开始推荐”，以获得当前“初筛后直接精读”流程的新结果。",
        ))

    render_recommendation_intermediate(result)

    st.subheader(tr("top3"))
    top3 = result.get("final_top3", [])
    if not top3:
        st.warning(bilingual_text("No recommendation passed the workflow.", "没有模型通过推荐流程。"))
    candidate_lookup = candidate_lookup_by_instance(result)
    for row in top3:
        candidate = candidate_lookup.get(row.get("instance_name", ""), {})
        render_top3_model_card(row, candidate.get("kg_info", {}))


def _format_score_percent(value) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value or "")
    return f"{numeric:.2f}%"


def render_validation_metric_cards(summary_df: pd.DataFrame) -> None:
    if summary_df is None or summary_df.empty:
        return
    metric_col = next((col for col in summary_df.columns if "Metric" in col or "指标" in col), summary_df.columns[0])
    percent_col = next((col for col in summary_df.columns if "(%)" in col), None)
    score_col = next((col for col in summary_df.columns if col.lower().strip() in {"score", "average score"}), None)
    columns = st.columns(min(3, len(summary_df)))
    for index, (_, row) in enumerate(summary_df.iterrows()):
        label = translate_value(str(row.get(metric_col, "")))
        if percent_col:
            value = _format_score_percent(row.get(percent_col, ""))
        elif score_col:
            try:
                value = _format_score_percent(float(row.get(score_col, 0)) * 100)
            except (TypeError, ValueError):
                value = str(row.get(score_col, ""))
        else:
            value = ""
        columns[index % len(columns)].metric(label or f"Metric {index + 1}", value)


def render_validation2_recommendation_validation_tab():
    enterprise_count = sum(
        item["requirement_id"].startswith("R") for item in USER_REQUIREMENTS
    )
    motivation_count = sum(
        item["requirement_id"].startswith("M") for item in USER_REQUIREMENTS
    )
    total_count = len(USER_REQUIREMENTS)
    st.caption(bilingual_text(
        f"Current canonical set: {total_count} requirements = "
        f"{enterprise_count} enterprise requirements + "
        f"{motivation_count} motivation requirements.",
        f"当前权威集合：{total_count} 个需求 = {enterprise_count} 个企业需求 + "
        f"{motivation_count} 个 motivation 需求。",
    ))
    if VALIDATION2_ACCURACY_SUMMARY_CSV.exists():
        summary_df = pd.read_csv(VALIDATION2_ACCURACY_SUMMARY_CSV)
        render_validation_metric_cards(summary_df)
        st.divider()
    if st.button(tr("validation_run"), type="primary", width="stretch"):
        with st.spinner(bilingual_text("Recalculating Validation2.0 metrics...", "正在重新计算 Validation2.0 指标...")):
            evaluate_validation2_accuracy(save=True)
        st.success(bilingual_text("Validation2.0 metrics recalculated.", "Validation2.0 指标已重新计算。"))

    for label, path in [
        (bilingual_text("Metric summary", "指标汇总"), VALIDATION2_ACCURACY_SUMMARY_CSV),
        (bilingual_text("Ranking-accuracy metric value for each requirement", "每个需求的ranking准确率指标值"), VALIDATION2_ACCURACY_BY_REQUIREMENT_CSV),
        (bilingual_text("Top-3 ranking recommendation result for each requirement", "每个需求的top3ranking推荐结果"), VALIDATION2_TOP3_CSV),
        (bilingual_text("Human Gold for all 54 requirements", "54 条需求统一人工推荐 Gold"), RECOMMENDATION_HUMAN_GOLD_CSV),
    ]:
        with st.expander(label, expanded=path == VALIDATION2_ACCURACY_SUMMARY_CSV):
            if path.exists():
                df = pd.read_csv(path)
                if path == VALIDATION2_ACCURACY_SUMMARY_CSV:
                    df = localize_dataframe(df)
                safe_dataframe(df, height=420)
                st.download_button(
                    bilingual_text(f"Download {path.name}", f"下载 {path.name}"),
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime="text/csv",
                    key=f"download_{path.name}",
                )
            else:
                st.warning(f"{bilingual_text('Missing file', '文件不存在')}: {path}")

def render_paper_ingestion_metric_cards(summary_df: pd.DataFrame) -> None:
    """Show the two primary paper-ingestion validation metrics."""
    if summary_df is None or summary_df.empty:
        return
    required = {
        "overall_average_semantic_similarity",
        "overall_factual_accuracy",
    }
    if not required.issubset(summary_df.columns):
        return
    row = summary_df.iloc[0]
    similarity = row["overall_average_semantic_similarity"]
    accuracy = row["overall_factual_accuracy"]
    columns = st.columns(2)
    try:
        similarity_text = f"{float(similarity) * 100:.2f}%"
    except (TypeError, ValueError):
        similarity_text = str(similarity or "")
    try:
        accuracy_text = f"{float(accuracy) * 100:.2f}%"
    except (TypeError, ValueError):
        accuracy_text = str(accuracy or "")
    columns[0].metric(
        bilingual_text(
            "Overall average semantic similarity",
            "35篇总体平均语义相似度",
        ),
        similarity_text,
    )
    columns[1].metric(
        bilingual_text("Field accuracy", "字段准确率"),
        accuracy_text,
    )


def render_paper_ingestion_semantic_validation_tab():
    st.subheader(bilingual_text("Paper-ingestion quality validation", "论文录入质量验证"))
    st.write(bilingual_text(
        "Purpose: treat 35 human-curated PaperModel records as the Gold Standard and evaluate the corresponding 35 LLM-ingested records field by field.",
        "目的：将35篇人工录入的 PaperModel 记录作为 Gold Standard，对对应的35篇 LLM 录入记录进行逐字段评估。",
    ))
    st.info(bilingual_text(
        "Method: faithfully translate and cache human Gold fields in English, then directly compare each complete Gold field with its corresponding complete LLM field using multilingual sentence embeddings. No field is converted to a canonical label. Field accuracy is independently judged by the configured LLM API.",
        "方法：先将人工 Gold 字段保真翻译成英文并缓存，再使用多语言句向量直接比较每个完整 Gold 字段与对应的完整 LLM 字段。任何字段都不会转换成规范化标签。字段准确率仍由已配置的 LLM API 独立进行事实判断。",
    ))
    st.caption(bilingual_text(
        "Missing-value and accuracy rules: values such as None, None reported, and Not reported are treated as absent. If either side is absent, the field is skipped for both semantic averaging and factual accuracy. Otherwise, similarity is descriptive and the LLM independently judges factual correctness. Translation and factual judgments are cached.",
        "缺失值与准确率规则：`None`、`None reported`、`Not reported` 等均视为空值。任意一方缺失时，该字段同时退出语义平均值和事实准确率计算；双方都有值时，相似度只作描述，事实正确性由 LLM 独立判断。翻译和事实判断结果都会缓存。",
    ))
    st.caption(bilingual_text(
        f"Saved output folder: {PAPER_INGESTION_QUALITY_VALIDATION_DIR}",
        f"结果保存文件夹：{PAPER_INGESTION_QUALITY_VALIDATION_DIR}",
    ))

    if st.button(
        bilingual_text("Run paper-ingestion quality validation", "运行论文录入质量验证"),
        type="primary",
        width="stretch",
        key="run_paper_ingestion_semantic_validation",
    ):
        progress_bar = st.progress(
            0,
            text=bilingual_text(
                "Preparing paper-ingestion quality validation...",
                "正在准备论文录入质量验证...",
            ),
        )
        stage_box = st.empty()
        stage_log = []

        def update_progress(progress, message_en, message_zh):
            message = bilingual_text(message_en, message_zh)
            progress_bar.progress(progress, text=message)
            stage_box.info(message)
            stage_log.append(
                {
                    "Progress / 进度": f"{progress}%",
                    "Stage / 阶段": message,
                }
            )
            st.session_state["paper_semantic_stage_log"] = stage_log

        try:
            with st.spinner(bilingual_text(
                "Translating Gold records, calculating semantic similarity, and running LLM factual field judgments...",
                "正在翻译 Gold 记录、计算语义相似度并执行 LLM 字段事实判断...",
            )):
                latest_semantic_evaluation = importlib.reload(
                    semantic_evaluation_module
                )
                latest_semantic_evaluation.run_paper_ingestion_semantic_validation(
                    save=True,
                    progress_callback=update_progress,
                )
            stage_box.success(bilingual_text(
                "All 35 papers and 980 configured field pairs have been processed.",
                "35篇论文和980个配置字段对已全部处理完成。",
            ))
            st.success(bilingual_text(
                "Paper-ingestion quality validation finished and saved.",
                "论文录入质量验证已完成并保存。",
            ))
        except Exception as exc:
            st.error(bilingual_text(
                f"Validation could not finish: {exc}",
                f"验证未能完成：{exc}",
            ))
            return

    stage_log = st.session_state.get("paper_semantic_stage_log", [])
    if stage_log:
        with st.expander(
            bilingual_text("Validation workflow", "验证运行流程"),
            expanded=True,
        ):
            safe_dataframe(pd.DataFrame(stage_log), height=300)

    output_files = [
        (bilingual_text("Overall validation summary", "验证总体汇总"), PAPER_INGESTION_VALIDATION_SUMMARY_CSV, True),
        (bilingual_text("Field-level semantic-similarity details", "字段级语义相似度明细"), PAPER_INGESTION_SEMANTIC_SIMILARITY_DETAILS_CSV, True),
        (bilingual_text("Field-level factual-accuracy details", "字段级事实准确率明细"), PAPER_INGESTION_FACTUAL_ACCURACY_DETAILS_CSV, True),
    ]

    if PAPER_INGESTION_VALIDATION_SUMMARY_CSV.exists():
        summary_df = pd.read_csv(PAPER_INGESTION_VALIDATION_SUMMARY_CSV)
        expected_columns = {
            "validation_status",
            "overall_average_semantic_similarity",
            "overall_factual_accuracy",
        }
        if expected_columns.issubset(summary_df.columns):
            render_paper_ingestion_metric_cards(summary_df)
        else:
            st.warning(bilingual_text(
                "The saved files use an older output layout. Run the updated validation to create the three current tables.",
                "当前保存文件使用旧版输出结构。请运行新版验证，生成当前三份表格。",
            ))
            return
    else:
        st.warning(bilingual_text(
            "No saved paper-ingestion quality-validation result is available yet. Click the run button above.",
            "尚未找到已保存的论文录入质量验证结果。请点击上方按钮运行。",
        ))

    for label, path, expanded in output_files:
        with st.expander(label, expanded=expanded):
            if path.exists():
                df = pd.read_csv(path)
                safe_dataframe(df, height=420)
                st.download_button(
                    bilingual_text(f"Download {path.name}", f"下载 {path.name}"),
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime="text/csv",
                    key=f"download_paper_semantic_{path.name}",
                )
            else:
                st.warning(f"{bilingual_text('Missing file', '文件不存在')}: {path}")


def render_validation2_tab():
    tab_recommendation, tab_paper_semantic = st.tabs([
        bilingual_text("Recommendation mechanism validation", "推荐机制验证"),
        bilingual_text("Paper-ingestion quality validation", "论文录入质量验证"),
    ])
    with tab_recommendation:
        render_validation2_recommendation_validation_tab()
    with tab_paper_semantic:
        render_paper_ingestion_semantic_validation_tab()


def render_validation_page():
    st.header(tr("validation"))
    render_validation2_tab()


def main():
    st.set_page_config(page_title="OPF Model KG GUI", layout="wide")
    st.session_state.setdefault("language_mode", "bilingual")
    language_mode = st.selectbox(
        tr("language"),
        ["bilingual", "zh", "en"],
        format_func=lambda value: {"bilingual": "English + 中文", "zh": "中文", "en": "English"}[value],
        key="language_mode",
    )
    st.title(tr("title"))
    st.caption(tr("caption"))

    page_labels = {
        key: text_for_mode(
            TEXT["en"].get(key, key),
            TEXT["zh"].get(key, key),
            language_mode,
        )
        for key in ["paper", "recommend", "validation"]
    }
    page = st.radio(
        tr("page"),
        ["paper", "recommend", "validation"],
        format_func=lambda key: page_labels[key],
        horizontal=True,
        key="page_choice",
    )
    if page == "paper":
        render_paper_page()
    elif page == "recommend":
        render_recommendation_page()
    else:
        render_validation_page()


if __name__ == "__main__":
    main()
