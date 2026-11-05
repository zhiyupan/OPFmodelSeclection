"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *

# PDF-to-PaperModel lookup.
# Given a paper PDF path, extract DOI/title clues, find the corresponding OPFModel instance in the OWL file, and print its complete information.

import re
import difflib
import xml.etree.ElementTree as ET


# Set this to the local PDF path you want to query.
PAPER_MODEL_QUERY_PDF_PATH = None
# Example:
# PAPER_MODEL_QUERY_PDF_PATH = PROJECT_ROOT / "paper" / "A_Hybrid_Data-Driven_Method_for_Fast_Solution_of_Security-Constrained_Optimal_Power_Flow.pdf"


PDF_LOOKUP_RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
PDF_LOOKUP_RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
PDF_LOOKUP_RDF_TYPE_TAG = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type"
PDF_LOOKUP_OWL_NAMED_INDIVIDUAL = "{http://www.w3.org/2002/07/owl#}NamedIndividual"


def pdf_lookup_local_name(resource):
    """Return local name from #Name, full OPF IRI, or slash/hash IRI."""
    if not resource:
        return ""
    if resource.startswith("#"):
        return resource[1:]
    if "OPF_IRI" in globals() and resource.startswith(OPF_IRI):
        return resource[len(OPF_IRI):]
    if "#" in resource:
        return resource.rsplit("#", 1)[1]
    return resource.rstrip("/").rsplit("/", 1)[-1]


def pdf_lookup_element_local_tag(element):
    """Return XML local tag name without namespace."""
    tag = element.tag
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def normalize_doi(value):
    """Normalize DOI text for exact DOI matching."""
    if not value:
        return ""
    value = str(value).strip().lower()
    value = value.replace("https://doi.org/", "").replace("http://doi.org/", "")
    value = value.replace("doi:", "").replace("doi：", "")
    value = value.strip(" .;,，。)")
    return value


def normalize_title(value):
    """Normalize title for fuzzy title matching."""
    if not value:
        return ""
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_doi_from_text(text):
    """Extract the first DOI-like string from text."""
    if not text:
        return ""
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, flags=re.IGNORECASE)
    if not match:
        return ""
    return normalize_doi(match.group(0))


def extract_pdf_title_and_doi(pdf_path, max_pages=3):
    """Extract title candidates and DOI from the first pages of a PDF."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_parts = []
    metadata_title = ""

    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        metadata_title = (doc.metadata or {}).get("title") or ""
        for page_index in range(min(max_pages, len(doc))):
            text_parts.append(doc[page_index].get_text("text"))
        doc.close()
    except Exception as exc:
        print("PyMuPDF PDF 读取失败，将只使用文件名线索 / PyMuPDF failed, using filename only:", type(exc).__name__, exc)

    pdf_text = "\n".join(text_parts)
    doi = extract_doi_from_text(pdf_text)

    title_candidates = []
    if metadata_title and normalize_title(metadata_title):
        title_candidates.append(metadata_title.strip())

    # Relatively long, nonempty, non-author-like lines near the top of the first page are useful title candidates.
    for raw_line in pdf_text.splitlines()[:60]:
        line = raw_line.strip()
        if len(line) < 12:
            continue
        if "@" in line or line.lower().startswith(("abstract", "index terms", "keywords")):
            continue
        if re.search(r"\b(university|department|school|institute|email)\b", line, flags=re.IGNORECASE):
            continue
        title_candidates.append(line)
        if len(title_candidates) >= 5:
            break

    filename_title = pdf_path.stem.replace("_", " ").replace("-", " ")
    if filename_title:
        title_candidates.append(filename_title)

    # Remove duplicates while preserving order.
    seen = set()
    unique_titles = []
    for title in title_candidates:
        key = normalize_title(title)
        if key and key not in seen:
            seen.add(key)
            unique_titles.append(title)

    return {
        "pdf_path": str(pdf_path),
        "doi": doi,
        "title_candidates": unique_titles,
        "text_preview": pdf_text[:1200],
    }


def is_pdf_lookup_opf_model_individual(individual_element):
    """Check whether a NamedIndividual is typed as OPFModel."""
    for child in list(individual_element):
        if child.tag != PDF_LOOKUP_RDF_TYPE_TAG:
            continue
        if pdf_lookup_local_name(child.attrib.get(PDF_LOOKUP_RDF_RESOURCE)) == "OPFModel":
            return True
    return False


def extract_pdf_lookup_individual_record(individual_element):
    """Extract all data/object properties from one OPFModel individual."""
    instance_name = pdf_lookup_local_name(individual_element.attrib.get(PDF_LOOKUP_RDF_ABOUT, ""))
    data_properties = {}
    object_properties = {}
    for child in list(individual_element):
        if child.tag == PDF_LOOKUP_RDF_TYPE_TAG:
            continue
        property_name = pdf_lookup_element_local_tag(child)
        if PDF_LOOKUP_RDF_RESOURCE in child.attrib:
            target = pdf_lookup_local_name(child.attrib.get(PDF_LOOKUP_RDF_RESOURCE))
            object_properties.setdefault(property_name, []).append(target)
        elif child.text is not None:
            data_properties[property_name] = child.text
    object_properties = {
        prop: sorted(set(values))
        for prop, values in object_properties.items()
    }
    return {
        "instance_name": instance_name,
        "data_properties": data_properties,
        "object_properties": object_properties,
    }


def load_all_pdf_lookup_opf_models(owl_path=INSTANCE_OWL_PATH):
    """Load all OPFModel individuals from the OWL XML."""
    read_path = resolve_instance_owl_read_path() if Path(owl_path) == INSTANCE_OWL_PATH else Path(owl_path)
    xml_text = read_path.read_text(encoding="utf-8")
    root = ET.fromstring(xml_text)
    records = []
    for individual in root.findall(f".//{PDF_LOOKUP_OWL_NAMED_INDIVIDUAL}"):
        if is_pdf_lookup_opf_model_individual(individual):
            records.append(extract_pdf_lookup_individual_record(individual))
    return records


def find_paper_model_by_pdf_metadata(pdf_info, owl_path=INSTANCE_OWL_PATH, min_title_similarity=0.82):
    """Find the most likely OPFModel individual by DOI first, then title similarity."""
    models = load_all_pdf_lookup_opf_models(owl_path)
    pdf_doi = normalize_doi(pdf_info.get("doi", ""))

    if pdf_doi:
        doi_matches = []
        for model in models:
            model_doi = normalize_doi(model["data_properties"].get("hasDOI", ""))
            if model_doi and model_doi == pdf_doi:
                doi_matches.append({
                    "match_type": "doi",
                    "score": 1.0,
                    "model": model,
                })
        if doi_matches:
            return doi_matches

    title_candidates = [normalize_title(title) for title in pdf_info.get("title_candidates", [])]
    title_candidates = [title for title in title_candidates if title]

    title_matches = []
    for model in models:
        model_title = normalize_title(model["data_properties"].get("hasPaperTitle", ""))
        model_name = normalize_title(model["data_properties"].get("hasModelName", ""))
        best_score = 0.0
        best_query_title = ""
        for query_title in title_candidates:
            for candidate_model_text in [model_title, model_name]:
                if not candidate_model_text:
                    continue
                score = difflib.SequenceMatcher(None, query_title, candidate_model_text).ratio()
                if query_title in candidate_model_text or candidate_model_text in query_title:
                    score = max(score, 0.90)
                if score > best_score:
                    best_score = score
                    best_query_title = query_title
        if best_score >= min_title_similarity:
            title_matches.append({
                "match_type": "title",
                "score": round(best_score, 4),
                "matched_pdf_title_candidate": best_query_title,
                "model": model,
            })
    title_matches.sort(key=lambda item: item["score"], reverse=True)
    return title_matches


def print_paper_model_full_record(match):
    """Print one matched OPFModel individual with all data/object properties."""
    model = match["model"]
    print("\n" + "=" * 90)
    print("匹配类型 / match type:", match.get("match_type"))
    print("匹配分 / match score:", match.get("score"))
    if match.get("matched_pdf_title_candidate"):
        print("PDF 标题候选 / matched PDF title candidate:", match.get("matched_pdf_title_candidate"))
    print("实例名 / instance_name:", model["instance_name"])

    print("\n数据属性与 metadata / Data properties and metadata")
    print("-" * 90)
    for key in sorted(model["data_properties"]):
        print(f"{key}: {model['data_properties'][key]}")

    print("\n对象属性关系 / Object property relations")
    print("-" * 90)
    for prop in sorted(model["object_properties"]):
        print(f"{prop}:")
        for target in model["object_properties"][prop]:
            print(f"  -> {target}")


def query_and_print_paper_model_from_pdf(pdf_path, owl_path=INSTANCE_OWL_PATH):
    """Main entry: query PaperModel instance by PDF path and print all KG information."""
    pdf_info = extract_pdf_title_and_doi(pdf_path)
    matches = find_paper_model_by_pdf_metadata(pdf_info, owl_path=owl_path)

    print("PDF 查询信息 / PDF query information")
    print("=" * 90)
    print("PDF 路径 / PDF path:", pdf_info["pdf_path"])
    print("提取 DOI / extracted DOI:", pdf_info["doi"] or "(none)")
    print("标题候选 / title candidates:")
    for title in pdf_info["title_candidates"]:
        print("  -", title)

    if not matches:
        print("\n没有在 OWL 中找到匹配的 OPFModel / PaperModel 实例。")
        print("No matching OPFModel / PaperModel individual found in OWL.")
        return {
            "pdf_info": pdf_info,
            "matches": [],
        }

    print("\n匹配到的实例数量 / matched individual count:", len(matches))
    for match in matches:
        print_paper_model_full_record(match)

    return {
        "pdf_info": pdf_info,
        "matches": matches,
    }
