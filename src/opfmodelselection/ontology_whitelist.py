"""Auto-extracted reusable definitions from the project notebooks.

Edit carefully: notebooks import these functions directly.
"""

from .config import *
from xml.etree import ElementTree as ET

# ============================================================
# Ontology-based whitelist lookup for paper-model extraction.
# ============================================================
#
# This LLM notebook reads OPF_Ontology2.0.owl directly instead of depending on the Python whitelist
# variables from Sections 3 and 4. It derives second-pass whitelists only for PaperModel object-property
# target classes from actual rdfs:subClassOf relationships; text-valued data properties no longer use taxonomy-enum whitelists.

import xml.etree.ElementTree as ET

OEO_CONSTRAINT_IRI = "https://openenergyplatform.org/ontology/oeo/OEO_00000104"
OEO_OBJECTIVE_FUNCTION_IRI = "https://openenergyplatform.org/ontology/oeo/OEO_00000304"
OEO_EXOGENOUS_DATA_IRI = "https://openenergyplatform.org/ontology/oeo/OEO_00030029"
OEO_ENERGY_TECHNOLOGY_IRI = "https://openenergyplatform.org/ontology/oeo/OEO_00020267"
OEO_ENERGY_DEMAND_SECTOR_IRI = "https://openenergyplatform.org/ontology/oeo/OEO_00000128"
OEO_COVERS_SECTOR_XML_TAG = "OEO_00000505"

RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
OWL_CLASS = "{http://www.w3.org/2002/07/owl#}Class"
RDFS_SUBCLASS_OF = "{http://www.w3.org/2000/01/rdf-schema#}subClassOf"

def unique_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def opf_resource_to_local_name_or_iri(resource):
    """Normalize #LocalName and full OPF IRI resources while preserving external IRIs."""
    if not resource:
        return None
    if resource.startswith("#"):
        return resource[1:]
    if "OPF_IRI" in globals() and resource.startswith(OPF_IRI):
        return resource[len(OPF_IRI):]
    return resource

def load_local_class_parent_map_from_owl(owl_path):
    """Read OPF-local and retained OEO class parent relations from OPF_Ontology2.0.owl."""
    root = ET.parse(owl_path).getroot()
    parent_map = {}
    for elem in root.findall(f".//{OWL_CLASS}"):
        about = elem.get(RDF_ABOUT)
        class_name = opf_resource_to_local_name_or_iri(about)
        if not class_name:
            continue
        parents = []
        for sub in elem.findall(RDFS_SUBCLASS_OF):
            parent = opf_resource_to_local_name_or_iri(sub.get(RDF_RESOURCE))
            if parent:
                parents.append(parent)
        parent_map[class_name] = unique_preserve_order(parent_map.get(class_name, []) + parents)
    return parent_map

def direct_children_from_parent_map(parent_map, parent_name_or_iri):
    return [
        class_name
        for class_name, parents in parent_map.items()
        if parent_name_or_iri in parents
    ]

def all_descendants_from_parent_map(parent_map, parent_name):
    descendants = []
    frontier = list(direct_children_from_parent_map(parent_map, parent_name))
    while frontier:
        current = frontier.pop(0)
        descendants.append(current)
        frontier.extend(direct_children_from_parent_map(parent_map, current))
    return unique_preserve_order(descendants)

def descendants_at_min_depth(parent_map, root_parent, min_depth=1):
    """Return descendant class IRIs/names at or below the requested tree depth."""
    results = []
    frontier = [(child, 1) for child in direct_children_from_parent_map(parent_map, root_parent)]
    while frontier:
        current, depth = frontier.pop(0)
        if depth >= min_depth:
            results.append(current)
        frontier.extend((child, depth + 1) for child in direct_children_from_parent_map(parent_map, current))
    return unique_preserve_order(results)

def load_class_labels_from_owl(owl_path):
    """Read labels for OPF and retained OEO whitelist classes."""
    root = ET.parse(owl_path).getroot()
    label_tag = "{http://www.w3.org/2000/01/rdf-schema#}label"
    labels = {}
    for elem in root.findall(f".//{OWL_CLASS}"):
        class_name = opf_resource_to_local_name_or_iri(elem.get(RDF_ABOUT))
        label_elem = elem.find(label_tag)
        if class_name and label_elem is not None and label_elem.text:
            labels[class_name] = label_elem.text.strip()
    return labels

def format_object_feature_whitelist(labels_by_class, property_to_classes):
    """Keep schema class identifiers exact while showing labels to the LLM."""
    lines = []
    for prop, choices in property_to_classes.items():
        readable = [f"{class_name} | label={labels_by_class.get(class_name, class_name)}" for class_name in choices]
        lines.append(f"{prop}: {readable}")
    return "\n".join(lines)

def level1_and_level2_map(parent_map, root_parent):
    level1 = direct_children_from_parent_map(parent_map, root_parent)
    level2_by_level1 = {
        level1_class: direct_children_from_parent_map(parent_map, level1_class)
        for level1_class in level1
    }
    level2_all = unique_preserve_order(
        class_name
        for children in level2_by_level1.values()
        for class_name in children
    )
    return level1, level2_by_level1, level2_all

def assert_required_ontology_whitelist_roots(parent_map):
    required = {
        "OPFModelFeature": "UserRequirement",
        "OPFParameterVariable": OEO_EXOGENOUS_DATA_IRI,
        "OPFModel": "https://openenergyplatform.org/ontology/oeo/OEO_00000314",
    }
    missing = []
    for class_name, parent in required.items():
        if parent not in parent_map.get(class_name, []):
            missing.append((class_name, parent, parent_map.get(class_name, [])))
    if missing:
        raise RuntimeError(
            "OPF_Ontology2.0.owl 的基层结构还没有正确写入。"
            "请检查/恢复 OPF_Ontology2.0.owl 与 OPF_Knowledge_Graph2.0.owl 中的核心 taxonomy/schema。缺失："
            + str(missing)
        )

OPF_ONTOLOGY_PARENT_MAP = load_local_class_parent_map_from_owl(BASE_OWL_PATH)
assert_required_ontology_whitelist_roots(OPF_ONTOLOGY_PARENT_MAP)

OBJECTIVE_LEVEL1_CLASSES, OBJECTIVE_LEVEL2_BY_LEVEL1, OBJECTIVE_LEVEL2_CLASSES = level1_and_level2_map(
    OPF_ONTOLOGY_PARENT_MAP,
    OEO_OBJECTIVE_FUNCTION_IRI,
)
CONSTRAINT_LEVEL1_CLASSES, CONSTRAINT_LEVEL2_BY_LEVEL1, CONSTRAINT_LEVEL2_CLASSES = level1_and_level2_map(
    OPF_ONTOLOGY_PARENT_MAP,
    OEO_CONSTRAINT_IRI,
)
PARAMETER_LEVEL1_CLASSES, PARAMETER_LEVEL2_BY_LEVEL1, PARAMETER_LEVEL2_CLASSES = level1_and_level2_map(
    OPF_ONTOLOGY_PARENT_MAP,
    "OPFParameterVariable",
)

FEATURE_PROPERTY_TO_RANGE = {
    # These PaperModel dimensions remain knowledge-graph object-property links.
    "hasMathematicalProblemType": "MathematicalProblemType",
    "hasModeledTechnology": OEO_ENERGY_TECHNOLOGY_IRI,
    "coversSector": OEO_ENERGY_DEMAND_SECTOR_IRI,
}

FEATURE_ALLOWED_CLASSES_BY_PROPERTY = {
    "hasMathematicalProblemType": all_descendants_from_parent_map(OPF_ONTOLOGY_PARENT_MAP, "MathematicalProblemType"),
    # Exclude broad OEO energy-technology root groups and retain more specific classes and their descendants.
    "hasModeledTechnology": descendants_at_min_depth(OPF_ONTOLOGY_PARENT_MAP, OEO_ENERGY_TECHNOLOGY_IRI, min_depth=2),
    "coversSector": all_descendants_from_parent_map(OPF_ONTOLOGY_PARENT_MAP, OEO_ENERGY_DEMAND_SECTOR_IRI),
}
ONTOLOGY_CLASS_LABELS = load_class_labels_from_owl(BASE_OWL_PATH)
