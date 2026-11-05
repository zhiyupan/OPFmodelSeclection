# 02 Online Recommendation Workflow

Primary entry point: the GUI's `Online recommendation` page. Notebook entry point: `src/Online_User_Requirement_Model_Selection.ipynb`.

Workflow: read the knowledge graph produced by the paper-ingestion workflow → accept a natural-language requirement → run grouped prefiltering → perform complete close reading → output the Top-3.

## 01_input

- `01_user_requirements.csv`: the sole authoritative natural-language requirement table, containing 54 entries: R01–R19 and M01–M35. The GUI example selector, online-recommendation Notebook, and batch Validation all read this file; the GUI still allows users to enter or rewrite any requirement interactively. Each row also stores one primary citation, a page or section reference, an evidence grade, and a concise mapping rationale.
- `02_requirement_source_traceability/`: the unified source-traceability directory, containing 28 enterprise/grid reports and a synchronized copy of the 36-paper manifest. Row-level citations in the authoritative 54-requirement table point directly to these materials. M01–M35 remain the fixed paper-motivation requirement set; the new P036 bibliography entry does not yet have a corresponding motivation requirement. The editable authoritative paper manifest is located in workflow 01 at `01_source_papers/paper_corpus_manifest.csv`, and the path preflight requires the two manifests to be byte-identical. This directory does not replace `01_user_requirements.csv` as the machine input.
- The four original 55-category requirement-design tables have been removed; they had no program consumer and could not be rigorously merged row by row with the 54 R/M cases.
- Cross-workflow input: `data/01_paper_ingestion_workflow/03_output/OPF_Knowledge_Graph2.0.owl`.

## 02_intermediate

- `01_validation_batch_full_run_records.json`: complete historical run records for the 54 recommendations, usable for auditing and reconstructing the currently saved Top-3 CSV. The existing 54 records belong to the legacy consistency-check workflow and do not contain the prompt/model fingerprints required by the current code, so the current batch program will not treat them as a resumable cache. Rerunning the workflow calls the API and generates records with the new fingerprints.

## 03_output

- `01_validation_batch_top3_recommendations.csv`: 54 requirements × Top-3, for 162 rows in total; this is the prediction input for recommendation Validation.

A single real-time recommendation in the GUI is retained only on the current session page and is not automatically appended to the batch files above. Selecting another canonical requirement, switching to custom input, or manually editing the requirement text immediately clears the previous requirement's intermediate results, Top-3, and execution selections so that a new requirement cannot continue displaying an old analysis. The existing batch JSON is an early consistency-check snapshot used for the thesis metrics; to obtain fresh results from the current direct prefilter → close reading workflow, rerun all 54 requirements.
