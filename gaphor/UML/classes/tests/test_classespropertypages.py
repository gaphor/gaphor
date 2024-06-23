import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.classespropertypages import (
    AttributesPage,
    ClassifierPropertyPage,
    Folded,
    InterfacePropertyPage,
    NamedElementPropertyPage,
    OperationsPage,
    ShowAttributesPage,
    ShowOperationsPage,
    attribute_model,
)


@pytest.fixture
def metaclass(element_factory):
    klass = element_factory.create(UML.Class)
    stereotype = element_factory.create(UML.Stereotype)
    UML.recipes.create_extension(klass, stereotype)
    return klass


def test_named_element_property_page(element_factory, event_manager):
    subject = element_factory.create(UML.Class)
    property_page = NamedElementPropertyPage(subject, event_manager)

    widget = property_page.construct()
    name_entry = find(widget, "name-entry")
    name_entry.set_text("Name")

    assert subject.name == "Name"


def test_no_named_element_property_page_for_metaclass(metaclass, event_manager):
    property_page = NamedElementPropertyPage(metaclass, event_manager)
    widget = property_page.construct()

    assert widget is None


def test_classifier_property_page(element_factory, event_manager):
    subject = element_factory.create(UML.Class)
    property_page = ClassifierPropertyPage(subject, event_manager)

    widget = property_page.construct()
    abstract = find(widget, "abstract")
    abstract.set_active(True)

    assert subject.isAbstract


def test_no_classifier_property_page_for_metaclass(metaclass, event_manager):
    property_page = ClassifierPropertyPage(metaclass, event_manager)
    widget = property_page.construct()

    assert widget is None


def test_interface_property_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = InterfacePropertyPage(item, event_manager)

    widget = property_page.construct()
    folded = find(widget, "folded")
    folded.set_active(True)

    assert item.folded == Folded.PROVIDED


def test_show_attributes_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = ShowAttributesPage(item, event_manager)

    widget = property_page.construct()
    show_attributes = find(widget, "show-attributes")
    show_attributes.set_active(False)

    assert not item.show_attributes


def test_attributes_page_add_attribute(element_factory, event_manager):
    subject = element_factory.create(UML.Interface)

    property_page = AttributesPage(subject, event_manager)

    property_page.construct()
    property_page.model.get_item(0).attribute = "+ attr: str"

    assert subject.attribute[0].name == "attr"
    assert subject.attribute[0].typeValue == "str"


def test_attribute_create_model(element_factory, event_manager):
    subject = element_factory.create(UML.Class)

    attr1 = element_factory.create(UML.Property)
    attr1.name = "attr1"
    subject.ownedAttribute = attr1
    attr2 = element_factory.create(UML.Property)
    attr2.name = "attr2"
    subject.ownedAttribute = attr2
    attr3 = element_factory.create(UML.Property)
    attr3.name = "attr3"
    subject.ownedAttribute = attr3

    list_store = attribute_model(subject, event_manager)

    assert list_store[0].attr is attr1
    assert list_store[1].attr is attr2
    assert list_store[2].attr is attr3


def test_show_operations_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.classes.InterfaceItem, subject=element_factory.create(UML.Interface)
    )
    property_page = ShowOperationsPage(item, event_manager)

    widget = property_page.construct()
    show_operations = find(widget, "show-operations")
    show_operations.set_active(False)

    assert not item.show_operations


def test_operations_page_add_operation(element_factory, event_manager):
    subject = element_factory.create(UML.Interface)

    property_page = OperationsPage(subject, event_manager)

    property_page.construct()
    property_page.model.get_item(0).operation = "+ oper()"

    assert subject.ownedOperation[0].name == "oper"
