import pytest

from gaphor.core.changeset.compare import UnmatchableModel, compare
from gaphor.core.modeling import Diagram, Element, ElementFactory, PendingChange
from gaphor.diagram.general.simpleitem import Box
from gaphor.UML import Class


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

    assert change.op == "add"
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"

    with open("conflict.gaphor", "w", encoding="utf-8") as f:
        f.write(saver())


def test_added_presentation(current, incoming):
    current_diagram = current.create(Diagram)
    diagram = incoming.create_as(Diagram, current_diagram.id)
    box = diagram.create(Box)

    change = next(compare(current, incoming))

    assert change.op == "add"
    assert change.element_id == box.id
    assert change.element_name == "Box"
    assert change.diagram_id == diagram.id


def test_added_element_with_attribute(current, incoming):
    diagram = incoming.create(Diagram)
    diagram.name = "Foo"

    vals = list(compare(current, incoming))
    elem_change, attr_change = vals

    assert elem_change.op == "add"
    assert elem_change.element_id == diagram.id
    assert elem_change.element_name == "Diagram"

    assert attr_change.op == "add"
    assert attr_change.element_id == diagram.id
    assert attr_change.property_name == "name"
    assert attr_change.property_value == "Foo"


def test_added_element_with_reference(current, incoming):
    diagram = incoming.create(Diagram)
    element = incoming.create(Element)
    current.create_as(Element, element.id)
    diagram.element = element

    change, ref_change, other_ref = list(compare(current, incoming))

    assert change.op == "add"
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"

    assert ref_change.op == "add"
    assert ref_change.element_id == diagram.id
    assert ref_change.property_name == "element"
    assert ref_change.property_ref == element.id

    assert other_ref.op == "add"
    assert other_ref.element_id == element.id
    assert other_ref.property_name == "ownedDiagram"
    assert other_ref.property_ref == diagram.id


def test_removed_element(current, incoming):
    diagram = current.create(Diagram)
    diagram.name = "Foo"

    change = next(compare(current, incoming))

    assert change.op == "remove"
    assert change.element_id == diagram.id
    assert change.element_name == "Diagram"


def test_changed_str_value(current, incoming):
    current_diagram = current.create(Diagram)
    current_diagram.name = "Old"
    incoming_diagram = incoming.create_as(Diagram, current_diagram.id)
    incoming_diagram.name = "New"

    change = next(compare(current, incoming))

    assert change.op == "update"
    assert change.element_id == current_diagram.id
    assert change.property_name == "name"
    assert change.property_value == "New"


def test_changed_int_value(current, incoming):
    current_class = current.create(Class)
    current_class.isAbstract = 0
    incoming_class = incoming.create_as(Class, current_class.id)
    incoming_class.isAbstract = 1

    change = next(compare(current, incoming))

    assert change.op == "update"
    assert change.element_id == current_class.id
    assert change.property_name == "isAbstract"
    assert change.property_value == "1"


def test_changed_none_value(current, incoming):
    current_diagram = current.create(Diagram)
    current_diagram.name = "Old"
    incoming_diagram = incoming.create_as(Diagram, current_diagram.id)
    incoming_diagram.name = None

    change = next(compare(current, incoming))

    assert change.op == "update"
    assert change.element_id == current_diagram.id
    assert change.property_name == "name"
    assert change.property_value is None


def test_changed_reference(current, incoming):
    current_diagram = current.create(Diagram)
    current_element = current.create(Element)
    incoming_diagram = incoming.create_as(Diagram, current_diagram.id)
    incoming_element = incoming.create_as(Element, current_element.id)
    incoming_diagram.element = incoming_element

    add_ref, update_ref = sorted(compare(current, incoming), key=lambda c: c.op)

    assert add_ref.op == "add"
    assert add_ref.element_id == incoming_element.id
    assert add_ref.property_name == "ownedDiagram"
    assert add_ref.property_ref == current_diagram.id

    assert update_ref.op == "update"
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
