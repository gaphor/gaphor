"""Parse a SysML Gaphor Model and generate a SysML data model."""

from collections import deque
from typing import Deque, Dict, List, Optional, Set, TextIO

from gaphor import UML
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.storage import storage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


def type_converter(association) -> Optional[str]:
    if association.typeValue is None:
        return None
        # raise ValueError(
        #     f"ERROR! type is not specified for property {association.name}"
        # )
    if association.typeValue.lower() == "boolean":
        return "int"
    elif association.typeValue.lower() in ("integer", "unlimitednatural"):
        return "int"
    elif association.typeValue.lower() == "string":
        return "str"
    else:
        return str(association.typeValue)


def write_attributes(cls: UML.Class, filename: TextIO) -> None:
    if not cls.attribute or not cls.attribute[0].name:
        filename.write("    pass\n\n")
    else:
        for a in cls.attribute["not it.association"]:  # type: ignore
            type_value = type_converter(a)
            filename.write(f"    {a.name}: attribute[{type_value}]\n")
        for a in cls.attribute["it.association"]:  # type: ignore
            filename.write(f"    {a.name}: association\n")
        for o in cls.ownedOperation:
            filename.write(f"    {o}: operation\n")


def breadth_first_search(tree: Dict, root) -> List:
    explored: List = []
    queue: Deque = deque()
    queue.appendleft(root)
    while queue:
        node = queue.popleft()
        if node not in explored:
            explored.append(node)
            neighbors = tree.get(node)
            if neighbors:
                for neighbor in neighbors:
                    queue.append(neighbor)
    explored.reverse()
    return explored


def generate(filename, outfile=None, overridesfile=None) -> None:
    element_factory = ElementFactory()
    modeling_language = UMLModelingLanguage()
    with open(filename):
        storage.load(
            filename, element_factory, modeling_language,
        )
    with open(outfile, "w") as f:
        trees: Dict = {}
        nontree_classes: List = []
        uml_directory: List = dir(UML.uml)
        uml_classes: List = []
        cls_added: Set = set()

        classes: List = element_factory.lselect(lambda e: e.isKindOf(UML.Class))
        for cls in classes:
            if cls.name not in cls_added and cls.name[0] != "~":
                if cls.name in uml_directory:
                    uml_classes.append(cls)
                elif not cls.general:
                    nontree_classes.append(cls)
                else:
                    trees[cls] = [g for g in cls.general]
                cls_added.add(cls.name)

        f.write(f"from gaphor.UML import Element\n")
        f.write(
            f"from gaphor.core.modeling.properties import attribute, " f"association\n"
        )
        for cls in uml_classes:
            f.write(f"from gaphor.UML import {cls.name}\n\n")

        cls_written: Set = set()

        for root in trees.keys():
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
        for cls in nontree_classes:
            if cls.name not in cls_written:
                f.write(f"class {cls.name}:\n")
                write_attributes(cls, filename=f)
                cls_written.add(cls.name)

        # stereotypes = element_factory.lselect(lambda e: isinstance(e,
        # UML.Stereotype))
        # for st in stereotypes:
        #     if st.name[0] != "~":
        #         meta = st.ownedAttribute["it.name == 'baseClass'"][
        #         :].association.ownedEnd.class_.name
        #         print(meta.name)
        #         f.write(f"class {st.name}:\n")
        #         write_attributes(st, filename=f)
        #         cls_names.add(st.name)

    element_factory.shutdown()
