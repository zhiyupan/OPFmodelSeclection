# Source papers and public bibliography

This folder contains two different kinds of files:

- `paper_corpus_manifest.csv` is the editable, canonical public bibliography for the 36 PaperModel records already stored in the knowledge graph. It lists P001–P036, titles, authors, years, DOIs, publisher pages, verified open-access links when available, licence notes, and historical local filenames. Git keeps this file.
- PDF files are local runtime inputs used only when adding, replacing, or reprocessing papers. Neither the original 35 third-party PDFs nor the newly added P036 PDF is included in the public repository, and Git ignores PDFs placed here.

Paper ingestion scans only `*.pdf`; it does not treat the CSV manifest as paper content. The project path preflight checks that the manifest exists and that it is byte-identical to the mirror at:

`data/02_online_recommendation_workflow/01_input/02_requirement_source_traceability/02_paper_corpus_manifest.csv`

Edit the canonical CSV here first, then copy it byte-for-byte to the workflow 02 mirror. This prevents the two workflows from silently showing different bibliographies.

Existing recommendation and Validation runs read the saved knowledge graph, not the original PDFs. A legally obtained local PDF is needed only when adding, replacing, or reprocessing a paper from scratch.
