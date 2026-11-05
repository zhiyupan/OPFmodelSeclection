# Input Description

- `01_recommendation_human_gold/recommendation_human_gold_54_requirements.csv`: the sole human Gold for online recommendation. R01–R19 use unordered acceptable candidate sets and are scored by the Top-3 hit proportion; M01–M35 use ordered models and the relevance weights in the table to calculate nDCG@3.
- `02_paper_ingestion_human_gold/01_records/`: 35 human-authored PaperModel Gold records for paper ingestion.

Cross-workflow inputs include workflow 02's authoritative CSV containing 54 requirements and its Top-3 CSV, together with workflow 01's knowledge graph. The source reports for enterprise requirements are stored in workflow 02's source-traceability directory. The authoritative paper manifest is stored in workflow 01 under `01_source_papers/`, while workflow 02 has a byte-for-byte identical reference mirror. These materials are no longer duplicated among the Validation inputs.
