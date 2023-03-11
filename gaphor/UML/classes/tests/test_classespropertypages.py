import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.classespropertypages import (
    AttributesPage,
    ClassAttributes,
    ClassifierPropertyPage,
    Folded,
    InterfacePropertyPage,
    NamedElementPropertyPage,
    OperationsPage,
)


@pytest.fixture
def metaclass(element_factory):
    klass = element_factory.create(UML.Class)
    stereotype = element_factory.create(UML.Stereotype)
    UML.recipes.create_extension(klass, stereotype)
    return klass


def test_named_element_property_page(element_factory):
    subject = element_factory.create(UML.Class)
    property_page = NamedElementPropertyPage(subject)

    widget = property_page.construct()
    name_entry = find(widget, "name-entry")
    name_entry.set_text("Name")

    assert subject.name == "Name"


def test_no_named_element_property_page_for_metaclass(metaclass):
    property_page = NamedElementPropertyPage(metaclass)
    widget = property_page.construct()

    assert widget is None


def test_classifier_property_page(element_factory):
    subject = element_factory.create(UML.Class)
    property_page = ClassifierPropertyPage(subject)

    widget = property_page.construct()
    abstract = find(widget, "abstract")
    abstract.set_active(True)

    assert subject.isAbstract


def test_no_classifier_property_page_for_metaclass(metaclass):
    property_page = ClassifierPropertyPage(metaclass)
    widget = property_page.construct()

    assert widget is None


def test_interface_property_page(diagram, element_factory):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = InterfacePropertyPage(item)

    widget = property_page.construct()
    folded = find(widget, "folded")
    folded.set_active(True)

    assert item.folded == Folded.PROVIDED


def test_attributes_page(diagram, element_factory):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = AttributesPage(item)

    widget = property_page.construct()
    show_attributes = find(widget, "show-attributes")
    show_attributes.set_active(False)

    assert not item.show_attributes


def test_attributes_page_add_attribute(diagram, element_factory):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = AttributesPage(item)

    property_page.construct()
    iter = property_page.model.get_iter((0,))
    property_page.model.update(iter, 0, "+ attr: str")

    assert item.subject.attribute[0].name == "attr"
    assert item.subject.attribute[0].typeValue == "str"


def test_attribute_reorder_after_dnd(diagram, element_factory):
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    attr1 = element_factory.create(UML.Property)
    attr1.name = "attr1"
    item.subject.ownedAttribute = attr1
    attr2 = element_factory.create(UML.Property)
    attr2.name = "attr2"
    item.subject.ownedAttribute = attr2
    attr3 = element_factory.create(UML.Property)
    attr3.name = "attr3"
    item.subject.ownedAttribute = attr3

    list_store = ClassAttributes(item)

    new_order = [attr3, attr1, attr2]
    list_store.sync_model(new_order)

    assert item.subject.ownedAttribute[0] is attr3
    assert item.subject.ownedAttribute[1] is attr1
    assert item.subject.ownedAttribute[2] is attr2


def test_operations_page(diagram, element_factory):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = OperationsPage(item)

    widget = property_page.construct()
    show_operations = find(widget, "show-operations")
    show_operations.set_active(False)

    assert not item.show_operations


def test_operations_page_add_operation(diagram, element_factory):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = OperationsPage(item)

    property_page.construct()
    iter = property_page.model.get_iter((0,))
    property_page.model.update(iter, 0, "+ oper()")

    assert item.subject.ownedOperation[0].name == "oper"
