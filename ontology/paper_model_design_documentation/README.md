# PaperModel Design and Traceability Documentation

This directory stores human-curated materials used while developing the PaperModel schema and taxonomies. It informs the design of the paper-ingestion workflow but is not a runtime input to that workflow.

- `01_taxonomy_source_tables/`: historical design source tables and literature references for objectives, constraints, parameters, and OPF types.

## Current Machine-Readable Authorities

- Ontology schema and level-1/level-2 taxonomies: `ontology/OPF_Ontology2.0.owl`
- PaperModel data fields and API JSON Schema: `src/opfmodelselection/paper_extraction.py`
- Pre-write schema validation: `src/opfmodelselection/paper_writer.py`
- Natural-language API prompts: the root-level `prompts.toml`

The runtime program does not scan or read any CSV, Markdown, or PDF files in this directory.
