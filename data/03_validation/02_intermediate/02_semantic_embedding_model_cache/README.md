# Semantic embedding model cache

This directory stores the local sentence-embedding model cache used by paper-ingestion Validation:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

It is used to calculate semantic similarity between the human Gold and knowledge-graph fields. If deleted, the program can download the approximately 458 MB model again when online; semantic-similarity validation cannot be rerun in an offline environment without it. The model files are excluded by `.gitignore`, and only this README is included in the public repository.
