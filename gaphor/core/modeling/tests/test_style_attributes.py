from gaphor import UML
from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.diagram import Diagram, StyledItem, attrname, lookup_attribute
from gaphor.UML.classes import ClassItem


def test_attribute_of_item(diagram):
    classitem = diagram.create(ClassItem)

    node = StyledItem(classitem)

    assert node.attribute("show_attributes") == "true"


def test_nonexistent_attribute_of_item(diagram):
    classitem = diagram.create(ClassItem)

    node = StyledItem(classitem)

    assert node.attribute("foobar") is None


def test_should_get_type_of_element_attribute(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    classitem = diagram.create(ClassItem, subject=class_)

    node = StyledItem(classitem)

    assert node.attribute("subject") == "class"


def test_should_read_attribute_of_subject(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    classitem = diagram.create(ClassItem, subject=class_)

    class_.name = "myname"
    node = StyledItem(classitem)

    assert node.attribute("name") == "myname"


# test attributes that can be any of a list
def test_nested_attribute_of_subject(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    attr: UML.Property = element_factory.create(UML.Property)
    class_.ownedAttribute = attr
    classitem = diagram.create(ClassItem, subject=class_)

    attr.name = "myname"
    attr.isStatic = 1
    node = StyledItem(classitem)

    assert node.attribute("attribute") == "property"
    assert node.attribute("attribute.name") == "myname"
    assert node.attribute("attribute.ownedElement") == ""
    assert node.attribute("attribute.isStatic") == "true"
    assert node.attribute("attribute.notAnAttribute") is None


def test_multiple_nested_attribute_of_subject(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    attr1 = element_factory.create(UML.Property)
    attr2 = element_factory.create(UML.Property)
    class_.ownedAttribute = attr1
    class_.ownedAttribute = attr2
    classitem = diagram.create(ClassItem, subject=class_)

    attr1.name = "first"
    attr2.name = "second"
    node = StyledItem(classitem)

    assert node.attribute("attribute") == "property property"
    assert node.attribute("attribute.name") in ("first second", "second first")
    assert node.attribute("attribute.notAnAttribute") is None


def test_mixed_case_attributes(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    attr1 = element_factory.create(UML.Property)
    class_.ownedAttribute = attr1
    classitem = diagram.create(ClassItem, subject=class_)

    attr1.name = "first"
    node = StyledItem(classitem)

    assert node.attribute("ownedattribute") == "property"
    assert node.attribute("ownedattribute.name") == "first"


def test_get_existing_attribute():
    diagram = Diagram()
    diagram.diagramType = "Test"

    assert diagram.diagramType == "Test"
    assert lookup_attribute(diagram, "diagramType") == "test"
    assert lookup_attribute(diagram, "owner") == ""


def test_non_existent_attribute():
    diagram = Diagram()

    assert lookup_attribute(diagram, "doesnotexist") is None


def test_nested_attribute():
    diagram = Diagram()
    diagram.ownedDiagram = Diagram()

    assert lookup_attribute(diagram, "ownedDiagram.name") == ""
    assert lookup_attribute(diagram, "ownedDiagram.doesnotexist") is None


def test_non_existent_nested_attribute():
    diagram = Diagram()

    assert lookup_attribute(diagram, "ownedDiagram.name") is None
    assert lookup_attribute(diagram, "ownedDiagram.doesnotexist") is None


def test_attrname_diagram_subject():
    diagram = Diagram()
    assert attrname(diagram, "subject") == "subject"


def test_attrname_collection_subject(diagram):
    collection1 = collection(None, None, int)
    assert attrname(collection1, "subject") == "subject"
