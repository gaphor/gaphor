"""A simple XMI importer.

The importer is used to import the static (meta)model from
XMI files.

It's purpose is to help code generation directly from the
official XMI files.
"""

import logging
from pathlib import Path
from xml.etree import ElementTree as etree

from gaphor import UML
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.diagram.group import group
from gaphor.storage import save
from gaphor.UML.modelinglanguage import UMLModelingLanguage

log = logging.getLogger(__name__)

modeling_language = UMLModelingLanguage()


class xmlns:
    xmi = "{http://www.omg.org/spec/XMI/20161101}"
    xsi = "{http://www.w3.org/2001/XMLSchema-instance}"
    uml = "{http://www.omg.org/spec/UML/20161101}"
    mofext = "{http://www.omg.org/spec/MOF/20161101}"


def create_element(elem: etree.Element, element_factory: ElementFactory):
    for child in elem:
        match child.tag:
            case "ownedAttribute" | "ownedEnd" | "ownedLiteral" | "ownedParameter":
                element = create(child, element_factory)
                if "isDerived" in child.attrib:
                    element.isDerived = child.attrib["isDerived"] == "true"
                if "isOrdered" in child.attrib:
                    element.isOrdered = child.attrib["isOrdered"] == "true"
                yield element
            case "packagedElement" | "ownedOperation":
                element = create(child, element_factory)
                yield element
                for child_element in create_element(child, element_factory):
                    assert group(element, child_element)
            case (
                "bodyCondition"
                | "generalization"
                | "memberEnd"
                | "navigableOwnedEnd"
                | "ownedComment"
                | "ownedRule"
                | "packageImport"
                | "precondition"
                | "redefinedOperation"
            ):
                pass
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def create(elem: etree.Element, element_factory: ElementFactory) -> UML.Element:
    id = elem.attrib[f"{xmlns.xmi}id"]
    type_name = elem.attrib[f"{xmlns.xmi}type"]
    assert type_name.startswith("uml:")
    type = modeling_language.lookup_element(type_name.replace("uml:", ""))
    assert type, f"No type for {type_name}"
    element: UML.Element = element_factory.create_as(type, id=id)
    if "name" in elem.attrib:
        element.name = elem.attrib["name"]
    return element


def link_element(elem: etree.Element, element_factory: ElementFactory):
    element = element_factory[elem.attrib[f"{xmlns.xmi}id"]]
    for child in elem:
        match child.tag:
            case "generalization":
                assert isinstance(element, UML.Classifier)
                general = child.find("general")
                assert general is not None and general.tag == "general", general
                generalization = element_factory.create_as(
                    modeling_language.lookup_element("Generalization"),
                    id=child.attrib[f"{xmlns.xmi}id"],
                )
                generalization.general = element_factory[
                    general.attrib[f"{xmlns.xmi}idref"]
                ]
                # TODO: for SysML, cover case: <general href="https://www.omg.org/spec/KerML/20250201/KerML.xmi#Kernel-Interactions-Interaction"/>
                generalization.specific = element
            case "memberEnd":
                element.memberEnd = element_factory[child.attrib[f"{xmlns.xmi}idref"]]
            case "navigableOwnedEnd":
                element.navigableOwnedEnd = element_factory[
                    child.attrib[f"{xmlns.xmi}idref"]
                ]
            case "ownedAttribute" | "ownedEnd" | "ownedOperation" | "ownedParameter":
                link_feature(child, element_factory)
            case "packagedElement":
                link_element(child, element_factory)
            case "ownedComment" | "ownedLiteral" | "ownedRule" | "packageImport":
                pass
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def link_feature(elem: etree.Element, element_factory: ElementFactory):
    element = element_factory[elem.attrib[f"{xmlns.xmi}id"]]
    for child in elem:
        match child.tag:
            case "bodyCondition" | "ownedComment" | "ownedRule" | "precondition":
                pass
            case "association":
                element.association = element_factory[child.attrib[f"{xmlns.xmi}idref"]]
            case "defaultValue":
                element.defaultValue = create(child, element_factory)
                if (instance := child.find("instance")) is not None:
                    assert isinstance(element, UML.Parameter | UML.Property)
                    element.defaultValue.instance = element_factory[
                        instance.attrib[f"{xmlns.xmi}idref"]
                    ]
            case "lowerValue":
                element.lowerValue = create(child, element_factory)
                assert isinstance(element, UML.MultiplicityElement)
                element.lowerValue.value = int(child.attrib.get("value", 0))
            case "type":
                if idref := child.attrib.get(f"{xmlns.xmi}idref"):
                    element.type = element_factory[idref]
                elif (href := child.attrib.get("href")) and href.startswith(
                    "https://www.omg.org/spec/UML/20161101/PrimitiveTypes.xmi#"
                ):
                    element.typeValue = href.split("#")[1]
                else:
                    log.warning(
                        "No type idref. Have href instead: %s", child.attrib.get("href")
                    )
            case "upperValue":
                element.upperValue = create(child, element_factory)
                assert isinstance(element, UML.MultiplicityElement)
                upper = int(child.attrib.get("value", 1))
                element.upperValue.value = "*" if upper == -1 else upper
            case "redefinedOperation":
                element.redefinedOperation = element_factory[
                    child.attrib[f"{xmlns.xmi}idref"]
                ]
            case "redefinedProperty":
                element.redefinedProperty = element_factory[
                    child.attrib[f"{xmlns.xmi}idref"]
                ]
            case "subsettedProperty":
                subsetted = element_factory[child.attrib[f"{xmlns.xmi}idref"]]
                if subsetted is element:
                    log.warning("Property %s subsets itself", element)
                else:
                    element.subsettedProperty = element_factory[
                        child.attrib[f"{xmlns.xmi}idref"]
                    ]
            case "ownedParameter":
                pass
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def convert(filename: Path) -> ElementFactory:
    tree = etree.parse(filename)

    root = tree.getroot()
    assert root.tag == f"{xmlns.xmi}XMI"

    element_factory = ElementFactory()

    for elem in root:
        if elem.tag == f"{xmlns.uml}Package":
            id = elem.attrib[f"{xmlns.xmi}id"]
            package = element_factory.create_as(
                modeling_language.lookup_element("Package"), id=id
            )
            package.name = elem.attrib["name"]
            for child in create_element(elem, element_factory):
                assert group(package, child)
            link_element(elem, element_factory)
        elif elem.tag == f"{xmlns.mofext}Tag":
            pass
        else:
            raise ValueError(f"Unexpected top level element {elem}")

    return element_factory


def main(infile: str, outfile: str):
    element_factory = convert(Path(infile))

    with open(outfile, "w", encoding="utf-8") as f:
        save(f, element_factory)


if __name__ == "__main__":
    import sys

    infile = sys.argv[1]
    outfile = sys.argv[2]
