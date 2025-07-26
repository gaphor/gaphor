"""A simple XMI importer.

The importer is used to import the static (meta)model from
XMI files.

It's purpose is to help code generation directly from the
official XMI files.
"""

from xml.etree import ElementTree as etree

from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.diagram.group import group
from gaphor.storage import save
from gaphor.UML import Classifier, Element
from gaphor.UML.modelinglanguage import UMLModelingLanguage

UML = UMLModelingLanguage()


class xmlns:
    xmi = "{http://www.omg.org/spec/XMI/20161101}"
    xsi = "{http://www.w3.org/2001/XMLSchema-instance}"
    uml = "{http://www.omg.org/spec/UML/20161101}"
    mofext = "{http://www.omg.org/spec/MOF/20161101}"


def create_element(elem: etree.Element, element_factory: ElementFactory):
    for child in elem:
        match child.tag:
            case (
                "generalization"
                | "memberEnd"
                | "navigableOwnedEnd"
                | "ownedComment"
                | "ownedLiteral"
                | "ownedRule"
                | "packageImport"
            ):
                pass
            case "ownedAttribute" | "ownedEnd" | "ownedOperation":
                element = create(child, element_factory)
                if "isDerived" in child.attrib:
                    element.isDerived = child.attrib["isDerived"] == "true"
                yield element
            case "packagedElement":
                element = create(child, element_factory)
                yield element
                for child_element in create_element(child, element_factory):
                    assert group(element, child_element)
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def create(elem: etree.Element, element_factory: ElementFactory) -> Element:
    id = elem.attrib[f"{xmlns.xmi}id"]
    type_name = elem.attrib[f"{xmlns.xmi}type"]
    assert type_name.startswith("uml:")
    type = UML.lookup_element(type_name.replace("uml:", ""))
    element: Element = element_factory.create_as(type, id=id)
    if "name" in elem.attrib:
        element.name = elem.attrib["name"]
    return element


def link_element(elem: etree.Element, element_factory: ElementFactory):
    element = element_factory[elem.attrib[f"{xmlns.xmi}id"]]
    for child in elem:
        match child.tag:
            case "generalization":
                assert isinstance(element, Classifier)
                general = child.find("general")
                assert general is not None and general.tag == "general", general
                generalization = element_factory.create_as(
                    UML.lookup_element("Generalization"),
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
            case "ownedComment":
                pass
            case "ownedLiteral":
                pass
            case "ownedRule":
                pass
            case "packageImport":
                pass
            case "ownedAttribute" | "ownedEnd" | "ownedOperation":
                link_feature(child, element_factory)
            case "packagedElement":
                link_element(child, element_factory)
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def link_feature(elem: etree.Element, element_factory: ElementFactory):
    element = element_factory[elem.attrib[f"{xmlns.xmi}id"]]
    for child in elem:
        match child.tag:
            case (
                "bodyCondition"
                | "ownedComment"
                | "ownedRule"
                | "precondition"
                | "redefinedOperation"
                | "redefinedProperty"
                | "subsettedProperty"
            ):
                pass
            case "association":
                element.association = element_factory[child.attrib[f"{xmlns.xmi}idref"]]
            case "defaultValue":
                pass
            case "lowerValue":
                pass
            case "type":
                pass
            case "upperValue":
                pass
            case "ownedParameter":
                pass
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def convert(filename: str):
    tree = etree.parse(filename)

    root = tree.getroot()
    assert root.tag == f"{xmlns.xmi}XMI"

    element_factory = ElementFactory()

    for elem in root:
        if elem.tag == f"{xmlns.uml}Package":
            id = elem.attrib[f"{xmlns.xmi}id"]
            package = element_factory.create_as(UML.lookup_element("Package"), id=id)
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
    element_factory = convert(infile)

    with open(outfile, "w", encoding="utf-8") as f:
        save(f, element_factory)


if __name__ == "__main__":
    import sys

    infile = sys.argv[1]
    outfile = sys.argv[2]
