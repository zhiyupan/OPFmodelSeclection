# data: Inputs, Intermediate Artifacts, and Outputs for Three Workflows

This directory is no longer limited to run outputs. It is the unified data location for three workflows. Each workflow is divided into:

- `01_input`: inputs supplied manually or required in advance.
- `02_intermediate`: intermediate artifacts generated during execution that support resuming or rebuilding the workflow.
- `03_output`: the workflow's final output files.

```text
data/
├─ 01_paper_ingestion_workflow/          Paper PDFs → PaperModel knowledge graph
│  ├─ 01_input/
│  ├─ 02_intermediate/
│  └─ 03_output/
├─ 02_online_recommendation_workflow/    User requirements → Top-3 paper models
│  ├─ 01_input/
│  ├─ 02_intermediate/
│  └─ 03_output/
└─ 03_validation/                        Validation of the first two workflows
   ├─ 01_input/
   ├─ 02_intermediate/
   └─ 03_output/
```

## The Three Workflows at a Glance

| Workflow | Primary inputs | Intermediate artifacts | Final outputs |
|---|---|---|---|
| 01 Paper ingestion | Local paper PDFs awaiting ingestion; the authoritative public bibliography manifest for the 36 existing papers, provided for human reference | PDF text, images, tables, and extraction JSON generated at runtime for new papers (historical artifacts were removed; the current P036 processing artifacts are local and untracked) | The sole authoritative knowledge graph, `OPF_Knowledge_Graph2.0.owl` |
| 02 Online recommendation | The knowledge graph, real-time custom requirements or the authoritative set of 54 natural-language requirements; 28 enterprise reports and a synchronized copy of the paper manifest provide source traceability | 54 complete recommendation run records | 54 × Top-3, for a total of 162 rows |
| 03 Validation | Two types of human Gold, the knowledge graph, and the Top-3 results | Gold English-translation/factual-judgment caches and a semantic-model cache | Recommendation metrics; field-level semantic details, field-level factual details, and an overall summary |

## Single-Source-of-Truth Principle

- In the paper-ingestion workflow, `01_source_papers/` contains both the description of the local PDF staging area and the authoritative `paper_corpus_manifest.csv`. Git ignores third-party paper PDFs but retains the README and manifest.
- The source-traceability directory for workflow 02 stores 28 enterprise/grid reports and retains `02_paper_corpus_manifest.csv` as a synchronized copy of the manifest so that the 54 requirements can cite it directly.
- The two paper manifests must be byte-for-byte identical; `check_project_paths()` verifies this requirement. They are public bibliographic indexes rather than paper full-text inputs; paper ingestion still scans only PDFs.
- The historical design-source tables for objective functions, constraints, parameters, and OPF types are located in `ontology/paper_model_design_documentation/`; they are not workflow inputs.
- Only one copy of the knowledge graph is stored, in `01_paper_ingestion_workflow/03_output/`; online recommendation and Validation read it directly.
- The 54 natural-language requirements for online recommendation are stored only in `02_online_recommendation_workflow/01_input/01_user_requirements.csv`. The GUI example selector, the online-recommendation Notebook, and batch Validation all share this file. Each row also stores one verified report or paper citation. The original four 55-class design tables have been removed, and no second set of requirement tables is retained.
- The human Gold for recommendation is stored only in `03_validation/01_input/01_recommendation_human_gold/recommendation_human_gold_54_requirements.csv`, with one row for each of the 54 requirements.
- The human Gold for paper ingestion is stored only in `03_validation/01_input/02_paper_ingestion_human_gold/01_records/`.
- The 28 reports supporting the enterprise requirements are stored only in workflow 02 under `01_input/02_requirement_source_traceability/01_enterprise_grid_reports/`.
- The online-recommendation Top-3 results are stored only in workflow 02 under `03_output/`; Validation does not duplicate them.

The original 35 PDFs have been moved to a local archive outside the project, and the newly added P036 PDF is likewise a local-only runtime input excluded from the public repository. The knowledge graph now retains 36 structured PaperModel instances. Neither online recommendation nor the existing fixed 35-paper Validation benchmark depends on local PDFs. To re-extract a paper from scratch, obtain it again from a lawful source listed in the manifest or restore the corresponding PDF.

See the `README.md` for each workflow for detailed descriptions of its files.
