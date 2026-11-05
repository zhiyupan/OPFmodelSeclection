"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *
from .prompt_loader import render_prompt

# ============================================================
# PDF/image/table/OCR processing wrapper that preserves near-complete paper content without generating a summary.
# ============================================================

from pathlib import Path
import re
import json
import copy
import base64
import mimetypes
import xml.etree.ElementTree as ET

# Public clones contain the corpus manifest, not third-party PDFs. Set this to
# a local PDF before using the notebook's single-paper ingestion cells.
PAPER_PATH = None
# Example: PAPER_PATH = Path(r"C:\path\to\your_paper.pdf")

# Keep this as None for near-complete extraction; set an integer only when a paper exceeds the model context window.
MAX_PAPER_CHARS = None

# Limit the number of exported images sent to the multimodal LLM call.
# This is not the PDF-export limit; it caps the number of images sent to the downstream API and can be adjusted for paper complexity.
MAX_LLM_IMAGE_INPUTS = 30

# Some PDF figures are vector drawings, not embedded image objects.
# If get_images() finds no images, automatically render complete pages as images for the multimodal model.
RENDER_PAGE_IMAGES_WHEN_NO_EMBEDDED_IMAGES = True
MAX_RENDERED_PAGE_IMAGES = 20
PDF_PAGE_RENDER_ZOOM = 2.0

# Use OCR only as an automatic fallback when the PDF text layer is insufficient; otherwise the multimodal model inspects images directly.
AUTO_OCR_FALLBACK = True
MIN_TOTAL_TEXT_CHARS_WITHOUT_OCR = 8_000
MIN_AVG_PAGE_TEXT_CHARS_WITHOUT_OCR = 450


try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    fitz = None
    HAS_PYMUPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    pdfplumber = None
    HAS_PDFPLUMBER = False

try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    pytesseract = None
    HAS_PYTESSERACT = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False


def print_paper_processing_status():
    print("PDF 处理依赖状态 / PDF processing dependency status:")
    print(f"  PyMuPDF 文本/页面处理 / PyMuPDF (fitz): {HAS_PYMUPDF}")
    print(f"  pdfplumber 表格提取 / pdfplumber: {HAS_PDFPLUMBER}")
    print(f"  pytesseract OCR 备用识别 / pytesseract: {HAS_PYTESSERACT}")
    print(f"  Pillow 图像读取 / Pillow: {HAS_PIL}")
    if not all([HAS_PYMUPDF, HAS_PDFPLUMBER, HAS_PIL]):
        print("\n需要安装缺失依赖 / Install missing packages:")
        print("  安装命令 / install command: pip install pymupdf pdfplumber pillow pytesseract")
        print("若要更好识别公式，可考虑 Mathpix 或专门公式 OCR 服务 / For better formula extraction, consider Mathpix or a dedicated formula OCR service.")


def normalize_extracted_text(text):
    """Clean obvious PDF extraction noise while preserving paragraph/page content."""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def maybe_truncate_text(text, max_chars=None):
    """Only truncate when max_chars is explicitly set."""
    if max_chars is None:
        return text
    return text[:max_chars] if len(text) > max_chars else text


def estimate_page_count_from_text(text):
    """Estimate page count from [PAGE n] markers inserted during extraction."""
    return max(1, len(re.findall(r"\\[PAGE \\d+\\]", text or "")))


def should_run_ocr_fallback(text, page_count, images):
    """Decide whether image OCR is needed as fallback.

    Normal digital PDFs usually have enough text from PyMuPDF, so OCR would
    duplicate the multimodal image input and may add noisy text. Scanned PDFs
    or PDFs with a broken text layer usually have very little extracted text;
    in that case OCR is useful as a fallback.
    """
    if not AUTO_OCR_FALLBACK or not images:
        return False

    cleaned_text = re.sub(r"\\s+", "", text or "")
    total_chars = len(cleaned_text)
    avg_chars_per_page = total_chars / max(1, page_count)
    return (
        total_chars < MIN_TOTAL_TEXT_CHARS_WITHOUT_OCR
        or avg_chars_per_page < MIN_AVG_PAGE_TEXT_CHARS_WITHOUT_OCR
    )


def extract_pdf_text_mupdf(pdf_path, max_chars=MAX_PAPER_CHARS):
    """Extract near-complete text from a digital PDF using PyMuPDF."""
    if not HAS_PYMUPDF:
        raise ImportError("Install pymupdf to extract PDF text: pip install pymupdf")

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Paper file not found: {pdf_path}")

    document = fitz.open(str(pdf_path))
    pages = []
    for page_index, page in enumerate(document):
        page_text = page.get_text("text") or ""
        if page_text.strip():
            pages.append(f"\n\n[PAGE {page_index + 1}]\n{page_text.strip()}")
    document.close()

    text = normalize_extracted_text("\n".join(pages))
    return maybe_truncate_text(text, max_chars=max_chars)


def extract_pdf_images(pdf_path, output_dir, max_images_per_page=8):
    if not HAS_PYMUPDF:
        raise ImportError("Install pymupdf to extract images from PDF: pip install pymupdf")

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(str(pdf_path))
    extracted = []

    for page_index in range(len(document)):
        page = document[page_index]
        for image_index, img_info in enumerate(page.get_images(full=True)):
            if image_index >= max_images_per_page:
                break

            xref = img_info[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image.get("ext", "png")
            image_name = f"page{page_index+1}_img{image_index+1}.{ext}"
            image_path = images_dir / image_name
            image_path.write_bytes(image_bytes)

            extracted.append({
                "page": page_index + 1,
                "image_index": image_index + 1,
                "path": str(image_path),
                "ext": ext,
                "width": base_image.get("width"),
                "height": base_image.get("height"),
                "image_source": "embedded_image",
                "ocr_text": "",
            })

    document.close()
    return extracted


def extract_pdf_page_images(pdf_path, output_dir, max_pages=MAX_RENDERED_PAGE_IMAGES, zoom=PDF_PAGE_RENDER_ZOOM):
    """Render full PDF pages as PNG images for multimodal LLM input.

    This is needed when figures are stored as vector drawings or page content
    rather than embedded raster image objects. In those PDFs, page.get_images()
    can return an empty list even though the paper visibly contains figures.
    """
    if not HAS_PYMUPDF:
        raise ImportError("Install pymupdf to render PDF pages: pip install pymupdf")

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    page_images_dir = output_dir / "page_images"
    page_images_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(str(pdf_path))
    extracted = []
    matrix = fitz.Matrix(zoom, zoom)

    for page_index in range(min(len(document), max_pages)):
        page = document[page_index]
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image_name = f"page{page_index + 1}_render.png"
        image_path = page_images_dir / image_name
        pixmap.save(str(image_path))

        extracted.append({
            "page": page_index + 1,
            "image_index": page_index + 1,
            "path": str(image_path),
            "ext": "png",
            "width": pixmap.width,
            "height": pixmap.height,
            "image_source": "page_render",
            "ocr_text": "",
        })

    document.close()
    return extracted


def extract_pdf_tables(pdf_path, max_pages=20):
    if not HAS_PDFPLUMBER:
        raise ImportError("Install pdfplumber to extract PDF tables: pip install pdfplumber")

    pdf_path = Path(pdf_path)
    tables = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            if page_index >= max_pages:
                break
            for table_index, table in enumerate(page.extract_tables() or []):
                if not table:
                    continue
                rows = [[cell or "" for cell in row] for row in table]
                tables.append({
                    "page": page_index + 1,
                    "table_index": table_index + 1,
                    "rows": rows,
                })

    return tables


def ocr_image_text(image_path, lang="eng"):
    if not HAS_PYTESSERACT or not HAS_PIL:
        return ""

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return normalize_extracted_text(text or "")
    except Exception:
        return ""


def summarize_table(table_record, max_cells=30):
    rows = table_record.get("rows", [])
    row_count = len(rows)
    col_count = max(len(row) for row in rows) if rows else 0
    snippet_rows = rows[:min(3, len(rows))]
    snippet = " | ".join(", ".join(str(cell) for cell in row) for row in snippet_rows)
    return f"Page {table_record['page']} table {table_record['table_index']} with {row_count} rows and {col_count} columns. Example rows: {snippet}"


def build_llm_payload_from_paper_record(record, max_chars=MAX_PAPER_CHARS):
    """Build text + image inputs for multimodal LLM extraction."""
    paper_text = maybe_truncate_text(record["text"], max_chars=max_chars)
    table_summaries = "\n".join(summarize_table(table) for table in record.get("tables", []))

    image_summaries = []
    for image in record.get("images", [])[:MAX_LLM_IMAGE_INPUTS]:
        image_source = image.get("image_source", "embedded_image")
        label = f"Page {image['page']} {image_source} {Path(image['path']).name}"
        ocr_text = image.get("ocr_text", "").strip()
        if ocr_text:
            label += f" (OCR text: {ocr_text[:500].strip()})"
        image_summaries.append(label)

    prompt_text = render_prompt(
        "paper_processing.llm_payload.user",
        paper_name=record["paper_name"],
        paper_path=record["paper_path"],
        paper_text=paper_text,
        table_summaries=table_summaries or "No tables extracted.",
        image_summaries="; ".join(image_summaries) or "No images extracted.",
    )

    return {
        "prompt_text": prompt_text,
        "image_input_paths": [img["path"] for img in record.get("images", [])[:MAX_LLM_IMAGE_INPUTS]],
        "table_summaries": table_summaries,
        "image_summaries": image_summaries,
    }


def extract_paper_record(paper_path, output_dir=None, max_chars=MAX_PAPER_CHARS):
    paper_path = Path(paper_path)
    if not paper_path.exists():
        raise FileNotFoundError(f"Paper file not found: {paper_path}")

    if output_dir is None:
        output_dir = PAPER_PROCESSING_OUTPUT_DIR / paper_path.stem
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = paper_path.suffix.lower()
    if suffix == ".pdf":
        text = extract_pdf_text_mupdf(paper_path, max_chars=max_chars)
        images = extract_pdf_images(paper_path, output_dir)
        embedded_image_count = len(images)
        if RENDER_PAGE_IMAGES_WHEN_NO_EMBEDDED_IMAGES and embedded_image_count == 0:
            images = extract_pdf_page_images(paper_path, output_dir)
        tables = extract_pdf_tables(paper_path)

        page_count = estimate_page_count_from_text(text)
        run_ocr = should_run_ocr_fallback(text, page_count, images)
        for image in images:
            image["ocr_text"] = ocr_image_text(image["path"]) if run_ocr else ""
    elif suffix in {".txt", ".md"}:
        text = maybe_truncate_text(
            paper_path.read_text(encoding="utf-8", errors="ignore"),
            max_chars=max_chars,
        )
        images = []
        tables = []
    else:
        raise ValueError(f"Unsupported paper format: {suffix}. Use PDF, TXT, or MD.")

    record = {
        "paper_path": str(paper_path),
        "paper_name": paper_path.stem,
        "text": text,
        "tables": tables,
        "images": images,
        "embedded_image_count": embedded_image_count if suffix == ".pdf" else 0,
        "page_render_image_count": sum(1 for image in images if image.get("image_source") == "page_render"),
        "ocr_fallback_used": any(bool(image.get("ocr_text")) for image in images),
    }
    record["llm_payload"] = build_llm_payload_from_paper_record(record, max_chars=max_chars)
    return record


def save_paper_record(record, output_dir=None):
    output_dir = Path(output_dir or PAPER_PROCESSING_OUTPUT_DIR / record["paper_name"])
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path = output_dir / "paper_record.json"
    record["text_path"] = str(output_dir / "paper_text.txt")
    Path(record["text_path"]).write_text(record["text"], encoding="utf-8")
    portable_record = make_project_paths_portable(record)
    record_path.write_text(
        json.dumps(portable_record, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return record_path


def load_paper_record(record_path):
    record_path = Path(record_path)
    return json.loads(record_path.read_text(encoding="utf-8"))


