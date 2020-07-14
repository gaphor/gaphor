from gaphor import UML
from gaphor.core.modeling.diagram import StyledItem
from gaphor.UML.classes import ClassItem


def test_attribute_of_item(diagram):
    classitem = diagram.create(ClassItem)

    node = StyledItem(classitem)

    assert node.attribute("show_attributes") == "true"


def test_nonexistant_attribute_of_item(diagram):
    classitem = diagram.create(ClassItem)

    node = StyledItem(classitem)

    assert node.attribute("foobar") == ""


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
    attr = element_factory.create(UML.Property)
    class_.ownedAttribute = attr
    classitem = diagram.create(ClassItem, subject=class_)

    attr.name = "myname"
    attr.isService = 1
    node = StyledItem(classitem)

    assert node.attribute("attribute") == "property"
    assert node.attribute("attribute.name") == "myname"
    assert node.attribute("attribute.isBehavior") == ""
    assert node.attribute("attribute.isService") == "true"
    assert node.attribute("attribute.notAnAttribute") == ""


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
    assert node.attribute("attribute.notAnAttribute") == ""


def test_mixed_case_attributes(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    attr1 = element_factory.create(UML.Property)
    class_.ownedAttribute = attr1
    classitem = diagram.create(ClassItem, subject=class_)

    attr1.name = "first"
    node = StyledItem(classitem)

    assert node.attribute("ownedattribute") == "property"
    assert node.attribute("ownedattribute.name") == "first"
