# Ontology Directory

This directory stores the ontology schema, taxonomies, and external reference ontologies shared by paper ingestion, online recommendation, and validation. It does not store the mutable instance data produced by the paper-ingestion workflow.

## Authoritative Files in This Directory

- `OPF_Ontology2.0.owl`: the OPF ontology and the machine-readable authority for classes, properties, level-1 and level-2 taxonomies, and write-validation rules. The paper-ingestion program reads it to generate whitelists and validate PaperModel instances.
- `oeo-2.11.0/`: the local OEO reference ontology.
- `IEC-CIM-Ontology-main/`: the local CIM reference ontology.
- `paper_model_design_documentation/`: source tables documenting the ontology taxonomy design. They support research traceability and manual review but are not runtime inputs or configuration.
- `catalog-v001.xml`: local Protégé/XML Catalog resolution mappings. It provides ontology tools with local paths for the OPF ontology, knowledge-graph output, OEO, and CIM. It neither copies nor generates OWL files, and the GUI does not read it.

## Knowledge-Graph Location

The sole authoritative knowledge graph is located at:

`../data/01_paper_ingestion_workflow/03_output/OPF_Knowledge_Graph2.0.owl`

This is a physical, self-contained, integrated OWL file containing the ontology schema declarations and paper-derived `OPFModel` / `PaperModel` instances. It is not a README pointer, symbolic link, or copy of another knowledge graph in this directory. The paper-ingestion program writes directly to this file, while online recommendation and validation read the same file directly. Do not create a second knowledge-graph copy under `ontology/`, because the instance data in the two files could diverge.

Placing the knowledge graph under the workflow's `03_output/` directory is an intentional separation of responsibilities:

- `ontology/` manages the relatively stable, reusable schema, taxonomies, and external reference ontologies.
- `data/01_paper_ingestion_workflow/03_output/` manages the instance knowledge graph produced and continually updated by paper ingestion.

Although the knowledge graph uses the OWL format, its role in this project is the final data product of the paper-ingestion workflow. To inspect it in Protégé, open the file directly or locate it through this directory's `catalog-v001.xml`.

## Single Authority and Synchronization Boundary

The base ontology and integrated knowledge graph are separate physical files with different responsibilities: the former is the stable schema, while the latter is a mutable workflow output containing a schema snapshot and instances. Manually changing one does not automatically synchronize the other. If the base ontology changes in the future, update the integrated knowledge graph through an explicit synchronization or rebuild step rather than maintaining two conflicting schema copies manually.
