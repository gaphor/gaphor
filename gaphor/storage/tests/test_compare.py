import pytest

from gaphor.core.modeling import Diagram, Element, ElementFactory
from gaphor.storage.compare import ADD, REMOVE, compare


@pytest.fixture
def current():
    return ElementFactory()


@pytest.fixture
def incoming():
    return ElementFactory()


def test_empty_element_factories(current, incoming):
    change_set = list(compare(current, incoming))

    assert not change_set


def test_similar_element_factories(current, incoming):
    element = incoming.create(Element)
    current.create_as(Element, element.id)

    change_set = list(compare(current, incoming))

    assert not change_set


def test_added_element(current, incoming):
    diagram = incoming.create(Diagram)

    change = next(compare(current, incoming))

    assert change.type is ADD
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"
    assert change.element_type == Diagram


def test_added_element_with_attribute(current, incoming):
    diagram = incoming.create(Diagram)
    diagram.name = "Foo"

    elem_change, attr_change = list(compare(current, incoming))

    assert elem_change.type is ADD
    assert elem_change.element_id == diagram.id
    assert elem_change.element_name == "Diagram"
    assert elem_change.element_type == Diagram

    assert attr_change.type is ADD
    assert attr_change.element_id == diagram.id
    assert attr_change.property_name == "name"
    assert attr_change.property_value == "Foo"


def test_added_element_with_reference(current, incoming):
    diagram = incoming.create(Diagram)
    element = incoming.create(Element)
    current.create_as(Element, element.id)
    diagram.element = element

    change, ref_change = list(compare(current, incoming))

    assert change.type is ADD
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"
    assert change.element_type == Diagram

    assert ref_change.type is ADD
    assert ref_change.element_id == diagram.id
    assert ref_change.property_name == "element"
    assert ref_change.property_ref == element.id


def test_removed_element(current, incoming):
    diagram = current.create(Diagram)
    diagram.name = "Foo"

    change = next(compare(current, incoming))

    assert change.type is REMOVE
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"
    assert change.element_type == Diagram
