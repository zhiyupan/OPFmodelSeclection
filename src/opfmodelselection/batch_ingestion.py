"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *
from .pdf_processing import *
from .paper_extraction import *
from .paper_writer import *

import json

# Read PDFs in bulk from the project paper-materials directory and write new OPFModel instances
# to OPF_Knowledge_Graph2.0.owl; never write paper instances to the schema ontology OPF_Ontology2.0.owl.

import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# Set the maximum number of paper models absent from the current knowledge graph to write in this run.
BATCH_NEW_PAPER_WRITE_LIMIT = 1

# Whether to run the LLM-based high-confidence review in Section 8.8.
# Keep True to use the full offline workflow.
BATCH_RUN_HIGH_CONFIDENCE_REVIEW = True

# Whether to print the complete instance report after each paper is written.
BATCH_PRINT_WRITTEN_REPORT = True

PAPER_FOLDER = PAPER_DIR

BATCH_RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
BATCH_RDF_ABOUT = "{" + BATCH_RDF_NS + "}about"
BATCH_RDF_RESOURCE = "{" + BATCH_RDF_NS + "}resource"

def batch_local_name_from_resource(resource):
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

def batch_normalize_text(value):
    value = str(value or "").lower()
    value = value.replace("https://doi.org/", "").replace("http://doi.org/", "")
    value = re.sub(r"doi:\s*", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())

def batch_titles_match(candidate_title, existing_title):
    """
    Reliable title match only: exact normalized match or clear title containment.
    No fuzzy token similarity, model-name match, or instance-name match.
    """
    candidate_norm = batch_normalize_text(candidate_title)
    existing_norm = batch_normalize_text(existing_title)
    if not candidate_norm or not existing_norm:
        return False
    if candidate_norm == existing_norm:
        return True
    if len(existing_norm) >= 24 and existing_norm in candidate_norm:
        return True
    if len(candidate_norm) >= 24 and candidate_norm in existing_norm:
        return True
    return False

def batch_path_matches(identity_path, existing_path):
    """Reliable source-file match using absolute path or exact filename."""
    if not identity_path or not existing_path:
        return False
    identity = Path(identity_path)
    existing = Path(existing_path)
    try:
        if identity.resolve() == existing.resolve():
            return True
    except Exception:
        pass
    return identity.name.lower() == existing.name.lower()

def batch_extract_doi_from_text(text):
    text = str(text or "")
    matches = re.findall(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, flags=re.IGNORECASE)
    cleaned = []
    for match in matches:
        doi = match.strip().rstrip(".,;:)】]")
        doi = doi.replace("\n", "").replace(" ", "")
        if doi and doi not in cleaned:
            cleaned.append(doi)
    return cleaned[0] if cleaned else None

def batch_clean_title_candidate(value):
    value = str(value or "").strip()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" -_|")
    if not value:
        return None
    lower = value.lower()
    bad_fragments = [
        "microsoft word",
        "ieee",
        "arxiv",
        "abstract",
        "index terms",
        "keywords",
        "doi",
        "http",
        "www.",
        "@",
    ]
    if any(fragment in lower for fragment in bad_fragments):
        return None
    if len(value.split()) < 3:
        return None
    return value

def batch_extract_first_pages_text(paper_path, max_pages=2):
    paper_path = Path(paper_path)
    if paper_path.suffix.lower() in {".txt", ".md"}:
        return paper_path.read_text(encoding="utf-8", errors="ignore")[:8000]
    if "fitz" not in globals() or fitz is None:
        return ""
    chunks = []
    with fitz.open(str(paper_path)) as doc:
        for page_index in range(min(max_pages, doc.page_count)):
            chunks.append(doc.load_page(page_index).get_text("text"))
    return "\n".join(chunks)

def batch_extract_title_candidates_from_text(text, paper_path):
    candidates = []
    paper_path = Path(paper_path)
    stem_title = batch_clean_title_candidate(paper_path.stem.replace("_", " ").replace("-", " "))
    if stem_title:
        candidates.append(stem_title)

    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    before_abstract = []
    for line in lines[:80]:
        if line.lower().startswith(("abstract", "index terms", "keywords", "introduction")):
            break
        before_abstract.append(line)

    # Try one-line titles first.
    for line in before_abstract[:25]:
        candidate = batch_clean_title_candidate(line)
        if candidate and 4 <= len(candidate.split()) <= 22:
            candidates.append(candidate)

    # Try joining the first few title-like lines.
    title_like = []
    for line in before_abstract[:15]:
        if "@" in line or re.search(r"\b(university|department|school|institute|email)\b", line, flags=re.IGNORECASE):
            continue
        if batch_clean_title_candidate(line):
            title_like.append(line)
        if len(title_like) >= 3:
            break
    if title_like:
        joined = batch_clean_title_candidate(" ".join(title_like))
        if joined:
            candidates.append(joined)

    unique = []
    seen = set()
    for candidate in candidates:
        norm = batch_normalize_text(candidate)
        if norm and norm not in seen:
            seen.add(norm)
            unique.append(candidate)
    return unique

def batch_extract_pdf_identity_without_llm(paper_path):
    """Extract DOI/title candidates without calling LLM, used only for skip detection."""
    paper_path = Path(paper_path)
    first_text = batch_extract_first_pages_text(paper_path, max_pages=2)
    doi = batch_extract_doi_from_text(first_text)
    title_candidates = batch_extract_title_candidates_from_text(first_text, paper_path)

    if "fitz" in globals() and fitz is not None and paper_path.suffix.lower() == ".pdf":
        try:
            with fitz.open(str(paper_path)) as doc:
                meta_title = batch_clean_title_candidate((doc.metadata or {}).get("title"))
            if meta_title:
                title_candidates.insert(0, meta_title)
        except Exception:
            pass

    unique_titles = []
    seen = set()
    for title in title_candidates:
        norm = batch_normalize_text(title)
        if norm and norm not in seen:
            seen.add(norm)
            unique_titles.append(title)

    return {
        "paper_path": str(paper_path),
        "doi": doi,
        "title_candidates": unique_titles,
    }

def batch_is_opfmodel_element(individual_element):
    for child in individual_element:
        if child.tag.endswith("}type"):
            if batch_local_name_from_resource(child.attrib.get(BATCH_RDF_RESOURCE)) == "OPFModel":
                return True
    return False

def batch_read_existing_opfmodel_identities():
    xml_text = resolve_instance_owl_read_path().read_text(encoding="utf-8")
    root = ET.fromstring(xml_text)
    records = []
    for individual in root.iter():
        if not individual.tag.endswith("}NamedIndividual"):
            continue
        if not batch_is_opfmodel_element(individual):
            continue
        data = {}
        for child in individual:
            tag = child.tag.split("}", 1)[-1]
            if tag == "type":
                continue
            if child.attrib.get(BATCH_RDF_RESOURCE):
                continue
            data.setdefault(tag, []).append(child.text or "")
        records.append(
            {
                "iri": individual.attrib.get(BATCH_RDF_ABOUT, ""),
                "local_name": batch_local_name_from_resource(individual.attrib.get(BATCH_RDF_ABOUT, "")),
                "doi": "; ".join(data.get("hasDOI", [])),
                "title": "; ".join(data.get("hasPaperTitle", [])),
                "source_file_path": "; ".join(data.get("hasSourceFilePath", [])),
                "source_file_name": "; ".join(data.get("hasSourceFileName", [])),
            }
        )
    return records

def batch_find_existing_model_for_identity(identity):
    existing_records = batch_read_existing_opfmodel_identities()
    doi_norm = batch_normalize_text(identity.get("doi"))
    if doi_norm:
        for record in existing_records:
            if batch_normalize_text(record.get("doi")) == doi_norm:
                return record, "DOI exact match / DOI 精确匹配"

    identity_path = identity.get("paper_path")
    for record in existing_records:
        if batch_path_matches(identity_path, record.get("source_file_path")):
            return record, "source-file path match / 文件路径匹配"
        if batch_path_matches(identity_path, record.get("source_file_name")):
            return record, "source-file name match / 文件名匹配"

    title_candidates = identity.get("title_candidates", []) or []
    for candidate_title in title_candidates:
        for record in existing_records:
            if batch_titles_match(candidate_title, record.get("title")):
                return record, "title exact-or-contained match / 标题精确或包含匹配"

    return None, "not found / 未找到"

def batch_iter_paper_files(paper_folder=PAPER_FOLDER):
    paper_folder = Path(paper_folder)
    if not paper_folder.exists():
        raise FileNotFoundError(f"paper folder not found: {paper_folder}")
    return sorted(paper_folder.glob("*.pdf"), key=lambda path: path.name.lower())

def ingest_new_papers_from_folder(limit=BATCH_NEW_PAPER_WRITE_LIMIT):
    """Scan the source-paper input directory and write up to `limit` new instances."""
    paper_files = batch_iter_paper_files()
    if limit is None:
        limit = len(paper_files)
    limit = int(limit)
    if limit <= 0:
        raise ValueError("BATCH_NEW_PAPER_WRITE_LIMIT must be positive.")

    summary = {
        "paper_folder": str(PAPER_FOLDER),
        "total_pdf_files": len(paper_files),
        "target_new_writes": limit,
        "scanned": 0,
        "skipped_existing": [],
        "written": [],
        "failed": [],
    }

    print("批量论文入库开始 / Batch paper ingestion started")
    print("来源论文输入目录 / source-paper input directory:", PAPER_FOLDER)
    print("PDF 数量 / PDF count:", len(paper_files))
    print("本次最多新增写入 / max new writes:", limit)

    written_count = 0
    for paper_path in paper_files:
        if written_count >= limit:
            break

        summary["scanned"] += 1
        print("\n" + "=" * 96)
        print("扫描论文 / Scanning paper:", paper_path.name)

        try:
            identity = batch_extract_pdf_identity_without_llm(paper_path)
            print("非 LLM 识别 DOI / DOI without LLM:", identity.get("doi") or "None")
            print("非 LLM 标题候选 / Title candidates without LLM:", identity.get("title_candidates") or [])

            existing, match_reason = batch_find_existing_model_for_identity(identity)
            if existing:
                print("已存在，跳过 LLM 抽取 / Already exists, skipping LLM extraction.")
                print("匹配方式 / Match reason:", match_reason)
                print("已有实例 / Existing instance:", existing.get("local_name"))
                print("已有标题 / Existing title:", existing.get("title"))
                print("已有 DOI / Existing DOI:", existing.get("doi"))
                summary["skipped_existing"].append(
                    {
                        "paper_path": str(paper_path),
                        "identity": identity,
                        "existing": existing,
                        "match_reason": match_reason,
                    }
                )
                continue

            print("未找到已有实例，开始完整 LLM 离线写入流程。")
            globals()["PAPER_PATH"] = paper_path
            record = extract_paper_model_record(paper_path)
            if BATCH_RUN_HIGH_CONFIDENCE_REVIEW:
                record = review_and_prune_paper_model_record(record)
            record = write_single_paper_model_instance_to_ontology(record)
            written_count += 1

            if BATCH_PRINT_WRITTEN_REPORT:
                print_paper_model_instance_report(record)

            summary["written"].append(
                {
                    "paper_path": str(paper_path),
                    "written_instance_name": record.get("written_instance_name"),
                    "paper_model_record_path": record.get("paper_model_record_path"),
                    "duplicate_action": record.get("duplicate_handling_action"),
                }
            )

            # Small pause helps avoid back-to-back API bursts.
            time.sleep(0.5)

        except Exception as exc:
            print("处理失败 / Failed:", paper_path)
            print(type(exc).__name__ + ":", exc)
            summary["failed"].append(
                {
                    "paper_path": str(paper_path),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue

    print("\n" + "=" * 96)
    print("批量论文入库结束 / Batch paper ingestion finished")
    print("扫描文件数 / Scanned files:", summary["scanned"])
    print("新增写入数 / New written:", len(summary["written"]))
    print("已存在跳过 / Skipped existing:", len(summary["skipped_existing"]))
    print("失败数量 / Failed:", len(summary["failed"]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary
