# Output Notes

`OPF_Knowledge_Graph2.0.owl` is the sole final output of the paper-ingestion workflow and the authoritative knowledge graph shared by online recommendation and both validation workflows.

It is the actual, self-contained, integrated OWL file. It contains the ontology schema declarations from `ontology/OPF_Ontology2.0.owl` and the current 36 paper-generated `OPFModel` / `PaperModel` instances. It is not a README, shortcut, or copy pointing to `ontology/`; the paper-ingestion program updates this file directly, and the other workflows read the same file directly.

Do not create a second copy of the knowledge graph in another directory. `ontology/README.md` explains the respective roles of the base ontology, integrated knowledge graph, and Protégé catalog.
