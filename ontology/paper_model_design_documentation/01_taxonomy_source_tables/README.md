# PaperModel Ontology Taxonomy Design Source Archive

**These CSV files are neither inputs to the paper-ingestion workflow nor program configuration.** They preserve the human-curated materials and literature references used to construct the objective, constraint, parameter, and OPF model-type taxonomies for design traceability.

Each category retains two views with identical row sets in different orders:

- `*_complete.csv`: the complete table, preferred for reading and subsequent curation.
- `*_export_view.csv`: the original export order, retained for source traceability.

The four categories are objectives, constraints, parameters, and OPF model types. The current Python code, GUI, and Notebooks do not read these CSV files. The sole machine-readable taxonomy authority at runtime is the parent file `ontology/OPF_Ontology2.0.owl`; `ontology_whitelist.py` constructs the level-1 and level-2 whitelists directly from its `rdfs:subClassOf` relationships.
