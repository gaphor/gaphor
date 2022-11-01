import pytest

from gaphor.core.changeset.apply import ADD, REMOVE, UPDATE
from gaphor.core.changeset.compare import UnmatchableModel, compare
from gaphor.core.modeling import Diagram, Element, ElementFactory, PendingChange


@pytest.fixture
def current(element_factory):
    return element_factory


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


def test_added_element(current, incoming, saver):
    diagram = incoming.create(Diagram)

    change = next(compare(current, incoming))

    assert change.op is ADD
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"

    with open("conflict.gaphor", "w", encoding="utf-8") as f:
        f.write(saver())


def test_added_element_with_attribute(current, incoming):
    diagram = incoming.create(Diagram)
    diagram.name = "Foo"

    elem_change, attr_change = list(compare(current, incoming))

    assert elem_change.op is ADD
    assert elem_change.element_id == diagram.id
    assert elem_change.element_name == "Diagram"

    assert attr_change.op is ADD
    assert attr_change.element_id == diagram.id
    assert attr_change.property_name == "name"
    assert attr_change.property_value == "Foo"


def test_added_element_with_reference(current, incoming):
    diagram = incoming.create(Diagram)
    element = incoming.create(Element)
    current.create_as(Element, element.id)
    diagram.element = element

    change, ref_change, other_ref = list(compare(current, incoming))

    assert change.op is ADD
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"

    assert ref_change.op is ADD
    assert ref_change.element_id == diagram.id
    assert ref_change.property_name == "element"
    assert ref_change.property_ref == element.id

    assert other_ref.op is ADD
    assert other_ref.element_id == element.id
    assert other_ref.property_name == "ownedDiagram"
    assert other_ref.property_ref == diagram.id


def test_removed_element(current, incoming):
    diagram = current.create(Diagram)
    diagram.name = "Foo"

    change = next(compare(current, incoming))

    assert change.op is REMOVE
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"


def test_changed_value(current, incoming):
    current_diagram = current.create(Diagram)
    current_diagram.name = "Old"
    incoming_diagram = incoming.create_as(Diagram, current_diagram.id)
    incoming_diagram.name = "New"

    change = next(compare(current, incoming))

    assert change.op is UPDATE
    assert change.element_id == current_diagram.id
    assert change.property_name == "name"
    assert change.property_value == "New"


def test_changed_reference(current, incoming):
    current_diagram = current.create(Diagram)
    current_element = current.create(Element)
    incoming_diagram = incoming.create_as(Diagram, current_diagram.id)
    incoming_element = incoming.create_as(Element, current_element.id)
    incoming_diagram.element = incoming_element

    add_ref, update_ref = sorted(compare(current, incoming), key=lambda c: c.op)

    assert add_ref.op is ADD
    assert add_ref.element_id == incoming_element.id
    assert add_ref.property_name == "ownedDiagram"
    assert add_ref.property_ref == current_diagram.id

    assert update_ref.op is UPDATE
    assert update_ref.element_id == current_diagram.id
    assert update_ref.property_name == "element"
    assert update_ref.property_ref == incoming_element.id


def test_pending_changes_end_up_in_current_model(current, incoming):
    diagram = incoming.create(Diagram)
    element = incoming.create(Element)
    current.create_as(Element, element.id)
    diagram.element = element

    changes = set(compare(current, incoming))

    assert changes == set(current.select(PendingChange))


def test_types_should_match(current, incoming):
    current_diagram = current.create(Diagram)
    incoming.create_as(Element, current_diagram.id)

    with pytest.raises(UnmatchableModel):
        next(compare(current, incoming))
