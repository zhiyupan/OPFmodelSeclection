# Validation Intermediate Artifacts

This directory stores only the two types of cache that the program actually reuses when running Validation:

- `01_llm_validation_cache/`: English translations of the human Gold and field-by-field factual judgments. Retaining this cache avoids repeated calls to costly LLM APIs.
- `02_semantic_embedding_model_cache/`: the local sentence-embedding model. Retaining it allows semantic-similarity validation to be rerun offline.

The source-traceability materials for enterprise requirements belong to the online-recommendation workflow and are now consolidated under `data/02_online_recommendation_workflow/01_input/02_requirement_source_traceability/`; they are no longer mixed into the Validation intermediate layer.
