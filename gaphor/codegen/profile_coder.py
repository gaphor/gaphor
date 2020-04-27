"""Parse a SysML Gaphor Model and generate a SysML data model."""

from collections import deque
from typing import Deque, Dict, List, Optional, Set, TextIO

from gaphor import UML
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.storage import storage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


def type_converter(association, enumerations: Dict = {}) -> Optional[str]:
    type_value = association.typeValue
    if type_value is None:
        return None
        # raise ValueError(
        #     f"ERROR! type is not specified for property {association.name}"
        # )
    if type_value.lower() == "boolean":
        return "int"
    elif type_value.lower() in ("integer", "unlimitednatural"):
        return "int"
    elif type_value.lower() == "string":
        return "str"
    elif type_value.endswith("Kind") or type_value.endswith("Sort"):
        # e = list(filter(lambda e: e["name"] == type_value, list(enumerations.values())))[0]
        return None
    else:
        return str(type_value)


def write_attributes(cls: UML.Class, filename: TextIO) -> None:
    if not cls.attribute or not cls.attribute[0].name:
        filename.write("    pass\n\n")
    else:
        for a in cls.attribute["not it.association"]:  # type: ignore
            type_value = type_converter(a)
            filename.write(f"    {a.name}: attribute[{type_value}]\n")
        for a in cls.attribute["it.association"]:  # type: ignore
            type_value = type_converter(a)
            if a.name == "baseClass":
                meta_cls = a.association.ownedEnd.class_.name
                filename.write(f"    {meta_cls}: association\n")
            else:
                filename.write(f"    {a.name}: relation_one[{type_value}]\n")
        for o in cls.ownedOperation:
            filename.write(f"    {o}: operation\n")


def find_root_nodes(
    trees: Dict[UML.Class, List[UML.Class]], referenced: List[UML.Class]
) -> List[UML.Class]:
    """Find the root nodes of tree models.

    The root nodes aren't generalizing other UML.Class objects, but are being
    referenced by others through their own generalizations.

    """
    return [key for key, value in trees.items() if not value and key in referenced]


def breadth_first_search(
    trees: Dict[UML.Class, List[UML.Class]], root: UML.Class
) -> List[UML.Class]:
    """Perform Breadth-First Search."""

    explored: List[UML.Class] = []
    queue: Deque[UML.Class] = deque()
    queue.appendleft(root)
    while queue:
        node = queue.popleft()
        if node not in explored:
            explored.append(node)
            neighbors: List[UML.Class] = []
            for key, value in trees.items():
                if node in value:
                    neighbors.append(key)
            if neighbors:
                for neighbor in neighbors:
                    queue.appendleft(neighbor)
    return explored


def generate(filename, outfile=None, overridesfile=None) -> None:
    element_factory = ElementFactory()
    modeling_language = UMLModelingLanguage()
    with open(filename):
        storage.load(
            filename, element_factory, modeling_language,
        )
    with open(outfile, "w") as f:
        trees: Dict[UML.Class, List[UML.Class]] = {}
        referenced: List[UML.Class] = []
        uml_directory: List[str] = dir(UML.uml)
        uml_classes: List[UML.Class] = []

        classes: List = element_factory.lselect(lambda e: e.isKindOf(UML.Class))
        for idx, cls in enumerate(classes):
            if cls.name[0] == "~":
                classes.pop(idx)
        for cls in classes:
            if cls.name in uml_directory:
                uml_classes.append(cls)
            else:
                trees[cls] = [g for g in cls.general]
                for gen in cls.general:
                    referenced.append(gen)

        f.write(f"from gaphor.UML import Element\n")
        f.write(f"from gaphor.core.modeling.properties import attribute, association\n")
        f.write(
            f"from gaphor.core.modeling.properties import relation_one, relation_many\n"
        )
        for cls in uml_classes:
            f.write(f"from gaphor.UML import {cls.name}\n\n")

        cls_written: Set[Element] = set()
        root_nodes = find_root_nodes(trees, referenced)
        for root in root_nodes:
            cls_search: List = breadth_first_search(trees, root)
            for cls in cls_search:
                if cls.name not in cls_written:
                    if cls.general:
                        f.write(
                            f"class {cls.name}("
                            f"{', '.join(g.name for g in cls.general)}):\n"
                        )
                    else:
                        f.write(f"class {cls.name}:\n")
                    cls_written.add(cls.name)
                    write_attributes(cls, filename=f)

        for cls, generalizations in trees.items():
            if not generalizations:
                if cls.name not in cls_written:
                    f.write(f"class {cls.name}:\n")
                    write_attributes(cls, filename=f)
                    cls_written.add(cls.name)

    element_factory.shutdown()
