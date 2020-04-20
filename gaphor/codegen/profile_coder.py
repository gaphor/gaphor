"""Parse a SysML Gaphor Model and generate a SysML data model."""

from typing import List, Optional, Set

from gaphor import UML
from gaphor.application import Session
from gaphor.storage import storage


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


def write_attributes(cls: UML.Class, filename) -> None:
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


def generate(filename, outfile=None, overridesfile=None):
    services = [
        "element_dispatcher",
        "event_manager",
        "component_registry",
        "element_factory",
        "modeling_language",
    ]
    session = Session(services=services)
    element_factory = session.get_service("element_factory")
    modeling_language = session.get_service("modeling_language")
    with open(filename):
        storage.load(
            filename, factory=element_factory, modeling_language=modeling_language,
        )
    with open(outfile, "w") as f:
        classes = element_factory.lselect(lambda e: e.isKindOf(UML.Class))

        cls_names: Set = set()

        # Step 1: add imports
        f.write(f"from gaphor.UML import Element\n")
        f.write(f"from gaphor.core.modeling.properties import attribute, association\n")
        uml_names: List = dir(UML.uml)
        for cls in classes:
            if cls.name in uml_names:
                f.write(f"from gaphor.UML import {cls.name}\n\n")
                cls_names.add(cls.name)

        # Step 2: classes with no inheritance
        for cls in classes:
            if cls.name not in cls_names and cls.name[0] != "~" and not cls.general:
                f.write(f"class {cls.name}:\n")
                write_attributes(cls, filename=f)
                cls_names.add(cls.name)

        # Step 3: classes with inheritance
        for cls in classes:
            if cls.name not in cls_names and cls.name[0] != "~":
                f.write(
                    f"class {cls.name}({', '.join(g.name for g in cls.general)}):\n"
                )
                write_attributes(cls, filename=f)
                cls_names.add(cls.name)

    element_factory.shutdown()
    session.shutdown()
