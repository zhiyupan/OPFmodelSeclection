# 01 Paper Ingestion Workflow

Primary entry point: the GUI's `Paper ingestion` page. Notebook entry point: `src/OPFModel_KG_Paper_Ingestion.ipynb`.

Workflow: read paper PDFs → parse text, images, and tables → perform two-pass LLM extraction and review → obtain human confirmation → write to the knowledge graph.

## 01_input

- `01_source_papers/`: a local staging directory for papers that also stores the authoritative `paper_corpus_manifest.csv`. The public repository does not include the original 35 third-party PDFs or the newly added P036 PDF, but it retains the directory README and the manifest of 36 papers. New papers uploaded through the GUI are saved here, and batch ingestion scans only PDFs placed locally in this directory.
- The requirement-source directory for Workflow 02 retains a byte-for-byte identical mirror of the manifest for row-level citations by R14–R16, R19, and M01–M35. P036 is present in the bibliography but does not yet have a corresponding paper-motivation requirement. Path preflight checks verify that the two CSV files remain synchronized.

The only external documents passed to the paper-extraction process in this workflow are the PDFs being processed. The manifest is a public bibliographic index and is not parsed as paper content. The source tables used to design the classification are located in `ontology/paper_model_design_documentation/` and are not inputs. At runtime, the schema and level-1 and level-2 taxonomy come from `ontology/OPF_Ontology2.0.owl`; the code uses them to generate whitelists and validate writes.

## 02_intermediate

- `01_pdf_processing_outputs/`: a runtime-generated directory. Historical text, images, tables, and JSON for the original 35 papers have been removed. The newly generated DeepOPF-V processing directory for P036 currently exists only as an untracked local artifact and is not included in the public project. When a new paper is ingested, the program automatically creates a subdirectory for it and generates new intermediate files. These generated files are not currently covered by `.gitignore`, so you may decide whether to commit them.

## 03_output

- `OPF_Knowledge_Graph2.0.owl`: the sole authoritative knowledge graph, currently containing 36 PaperModel instances. Paper ingestion writes to it, while online recommendation and Validation read from it.

Ingestion-quality validation is located in `data/03_validation/` rather than this workflow because it belongs to the unified validation workflow.
