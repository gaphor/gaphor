"""A simple XMI importer.

The importer is used to import the static (meta)model from
XMI files.

It's purpose is to help code generation directly from the
official XMI files.

This importer is very oppinionated and tailored towards the
KerML and SysML 2 models provided by the OMG.
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


# These functions relies on the URL and id consistency of KerML identifiers.
# These functions should only be called when generating KerML derived models.
# Hrefs look like: "https://www.omg.org/spec/KerML/20250201/KerML.xmi#Kernel-Interactions-Interaction"


def create_class_from_href(href: str, element_factory: ElementFactory) -> UML.Class:
    uri, id = href.split("#")
    assert uri == "https://www.omg.org/spec/KerML/20250201/KerML.xmi"

    if class_ := element_factory.lookup(id):
        assert isinstance(class_, UML.Class)
        assert class_.owner.id == uri
        return class_

    if not (package := element_factory.lookup(uri)):
        package = element_factory.create_as(UML.Package, id=uri)
        package.name = "KerML"

    class_ = element_factory.create_as(UML.Class, id=id)
    class_.name = id.split("-")[-1]
    assert group(package, class_)
    return class_


def create_property_from_href(
    href: str, element_factory: ElementFactory
) -> UML.Property | None:
    uri, id = href.split("#")
    assert uri == "https://www.omg.org/spec/KerML/20250201/KerML.xmi"

    if "-A_" in id:
        # Property is owned by association, skip it
        return None

    if prop := element_factory.lookup(id):
        assert isinstance(prop, UML.Property)
        assert prop.owner.owner.id == uri
        return prop

    class_href, name = href.rsplit("-", 1)
    class_ = create_class_from_href(class_href, element_factory)

    prop = element_factory.create_as(UML.Property, id=id)
    prop.name = name
    class_.ownedAttribute = prop
    return prop


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
                generalization.general = (
                    element_factory[general.attrib[f"{xmlns.xmi}idref"]]
                    if f"{xmlns.xmi}idref" in general.attrib
                    else create_class_from_href(general.attrib["href"], element_factory)
                )
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


def link_feature(elem: etree.Element, element_factory: ElementFactory):  # noqa: C901
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
                    if idref := child.attrib.get(f"{xmlns.xmi}idref"):
                        assert isinstance(element, UML.Parameter | UML.Property)
                        element.defaultValue.instance = element_factory[
                            instance.attrib[f"{xmlns.xmi}idref"]
                        ]
                    elif "href" in child.attrib:
                        log.warning(
                            "should default value instance %s", child.attrib["href"]
                        )
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
                    element.type = create_class_from_href(
                        child.attrib["href"], element_factory
                    )
            case "upperValue":
                element.upperValue = create(child, element_factory)
                assert isinstance(element, UML.MultiplicityElement)
                upper = int(child.attrib.get("value", 1))
                element.upperValue.value = "*" if upper == -1 else upper
            case "redefinedOperation":
                if f"{xmlns.xmi}idref" in child.attrib:
                    element.redefinedOperation = element_factory[
                        child.attrib[f"{xmlns.xmi}idref"]
                    ]
                elif "href" in child.attrib:
                    log.warning("should redefine operation %s", child.attrib["href"])
            case "redefinedProperty":
                if f"{xmlns.xmi}idref" in child.attrib:
                    element.redefinedProperty = element_factory[
                        child.attrib[f"{xmlns.xmi}idref"]
                    ]
                elif "href" in child.attrib:
                    if prop := create_property_from_href(
                        child.attrib["href"], element_factory=element_factory
                    ):
                        element.redefinedProperty = prop
            case "subsettedProperty":
                if f"{xmlns.xmi}idref" in child.attrib:
                    subsetted = element_factory[child.attrib[f"{xmlns.xmi}idref"]]
                    if subsetted is element:
                        log.warning("Property %s subsets itself", element)
                    else:
                        element.subsettedProperty = element_factory[
                            child.attrib[f"{xmlns.xmi}idref"]
                        ]
                elif "href" in child.attrib:
                    if prop := create_property_from_href(
                        child.attrib["href"], element_factory=element_factory
                    ):
                        element.subsettedProperty = prop
            case "ownedParameter":
                pass
            case unsupported:
                raise ValueError(f"Unhandled tag {unsupported}")


def link_core_model(element_factory):
    if element := next(
        element_factory.select(
            lambda e: isinstance(e, UML.Class)
            and e.name == "Element"
            and e.owningPackage.name != "KerML"
        ),
        None,
    ):
        log.info("Element %s will inherit from Core.Base", element)

        core_package = next(
            element_factory.select(
                lambda e: isinstance(e, UML.Package)
                and e.name == "Core"
                and not e.owningPackage
            ),
            None,
        )
        if not core_package:
            core_package = element_factory.create(UML.Package)
            core_package.name = "Core"

        base_element = next(
            element_factory.select(
                lambda e: isinstance(e, UML.Class) and e.name == "Base"
            ),
            None,
        )
        if not base_element:
            base_element = element_factory.create(UML.Class)
            base_element.name = "Base"
            base_element.package = core_package

        generalization = element_factory.create(
            modeling_language.lookup_element("Generalization")
        )
        generalization.general = base_element
        generalization.specific = element


def patch_sysml2_model(element_factory: ElementFactory):
    """Apply some changes to make the SysML v2 model play well with out generator."""
    if prop := element_factory.lookup("Systems-Views-Expose-visibility"):
        prop.unlink()


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
            link_core_model(element_factory)
            patch_sysml2_model(element_factory)
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
