# Input Notes

The only runtime documents passed to the paper-extraction process in this workflow are the paper PDFs awaiting processing in `01_source_papers/`. The GUI reads these PDFs when adding, replacing, or re-ingesting papers, and the batch-processing Notebook also scans only PDFs in this directory.

The `paper_corpus_manifest.csv` in the same directory is the authoritative public bibliographic manifest for the 36 existing PaperModel instances. It contains P001–P036, titles, authors, years, DOIs, official sources, open-access links, licensing notes, and historical local filenames. It supports reader access and source traceability; the paper-extraction program does not treat it as paper content, and it is not a second knowledge graph. Workflow 02 retains a synchronized, byte-for-byte identical copy for references from the requirement tables. The original 35 paper PDFs have been moved to a local archive outside the project, and the P036 PDF is also a local-only runtime input; legally obtained local copies are needed only when reparsing the papers from scratch.

The design-source records for objective functions, constraints, parameters, and OPF types are located in `ontology/paper_model_design_documentation/` and are not inputs.
