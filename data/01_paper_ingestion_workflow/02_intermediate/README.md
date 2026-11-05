# Intermediate Results

`01_pdf_processing_outputs/` is the runtime-generated directory for paper parsing and LLM extraction. The project has completed knowledge-graph writes for 36 PaperModel instances. Text, images, tables, OCR information, and intermediate JSON from the original 35 papers have been removed. The newly generated DeepOPF-V processing outputs for P036 currently exist only as local untracked artifacts and are not part of the public project. Neither online recommendation nor Validation reads these files.

When a new paper is ingested, the program automatically creates intermediate artifacts under `01_pdf_processing_outputs/<PDF filename without extension>/`:

- The GUI and batch process save extracted images, `paper_model_record.json`, and the reviewed `paper_model_record_reviewed.json`. The paper text, tables, and OCR content are included in the JSON.
- If the Notebook runs the standalone PDF parsing and save step, it also generates `paper_text.txt` and `paper_record.json`.

The directory is created automatically. Reprocessing a paper with the same name overwrites files with matching names but does not clear the entire subdirectory first, so obsolete extra images from earlier runs require manual review. Deleting the subdirectory for a newly ingested paper does not damage its existing knowledge-graph instance, but it removes the review materials from that extraction run and incurs parsing and API costs again if the paper is reprocessed.
