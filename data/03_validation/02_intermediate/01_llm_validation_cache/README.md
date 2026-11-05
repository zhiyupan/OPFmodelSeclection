# LLM validation cache

This directory stores two types of costly, reusable intermediate artifacts for paper-ingestion Validation:

- `01_human_gold_english_translations.json`: a faithful English-translation cache for the human Gold covering 35 papers.
- `02_field_factual_judgments.json`: a field-by-field LLM factual-judgment cache for 35 papers.

The program validates source-field hashes, the prompt hash, and model information, and calls the API again only when a cache entry is invalid. Deleting these files does not damage the knowledge graph or saved results, but the next complete validation run will need to execute approximately 70 LLM tasks again. This takes time, may incur charges, and may cause slight result drift, so retaining the files is recommended.
