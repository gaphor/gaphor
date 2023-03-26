import pytest

from gaphor.core.changeset.compare import UnmatchableModel, compare, RefChange
from gaphor.core.modeling import (
    Diagram,
    Element,
    ElementFactory,
    PendingChange,
    StyleSheet,
)
from gaphor.diagram.general.simpleitem import Box
from gaphor.UML import Class, Property


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

    assert attr_change.op == "update"
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

    assert ref_change.op == "update"
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


@pytest.mark.parametrize(
    "type,name,current_value,incoming_value,expected_value",
    [
        [Diagram, "name", "Old", "New", "New"],
        [Diagram, "name", None, "New", "New"],
        [Diagram, "name", "Old", None, None],
        [Class, "isAbstract", 0, 1, "1"],
        [Class, "isAbstract", 1, 0, None],
    ],
)
def test_changed_value(
    current, incoming, type, name, current_value, incoming_value, expected_value
):
    current_element = current.create(type)
    setattr(current_element, name, current_value)
    incoming_element = incoming.create_as(type, current_element.id)
    setattr(incoming_element, name, incoming_value)

    change = next(compare(current, incoming))

    assert change.op == "update"
    assert change.element_id == current_element.id
    assert change.property_name == name
    assert change.property_value == expected_value


def test_changed_enumeration_with_default_value(current, incoming):
    current_property = current.create(Property)
    incoming.create_as(Property, current_property.id)
    current_property.aggregation = "shared"

    change = next(compare(current, incoming))

    assert change.op == "update"
    assert change.element_id == current_property.id
    assert change.property_name == "aggregation"
    assert change.property_value is None


def test_add_reference(current, incoming):
    current_diagram = current.create(Diagram)
    current_element = current.create(Element)
    incoming_diagram = incoming.create_as(Diagram, current_diagram.id)
    incoming_element = incoming.create_as(Element, current_element.id)
    incoming_diagram.element = incoming_element

    add_ref, update_ref = sorted(compare(current, incoming), key=lambda c: c.op)

    assert isinstance(add_ref, RefChange)
    assert add_ref.op == "add"
    assert add_ref.element_id == incoming_element.id
    assert add_ref.property_name == "ownedDiagram"
    assert add_ref.property_ref == current_diagram.id

    assert isinstance(update_ref, RefChange)
    assert update_ref.op == "update"
    assert update_ref.element_id == current_diagram.id
    assert update_ref.property_name == "element"
    assert update_ref.property_ref == incoming_element.id


def test_remove_reference(current, incoming):
    current_diagram = current.create(Diagram)
    current_element = current.create(Element)
    current_diagram.element = current_element
    incoming.create_as(Diagram, current_diagram.id)
    incoming_element = incoming.create_as(Element, current_element.id)

    remove_ref, other_ref = sorted(compare(current, incoming), key=lambda c: c.op)

    assert remove_ref.op == "remove"
    assert remove_ref.element_id == incoming_element.id
    assert remove_ref.property_name == "ownedDiagram"
    assert remove_ref.property_ref == current_diagram.id

    assert other_ref.op == "update"
    assert other_ref.element_id == current_diagram.id
    assert other_ref.property_name == "element"
    assert other_ref.property_ref is None


def test_remove_with_common_reference(current, incoming):
    current_diagram = current.create(Diagram)
    current_element = current.create(Element)
    current_diagram.element = current_element
    current_common = current.create(Diagram)
    current_common.element = current_element
    incoming.create_as(Diagram, current_diagram.id)
    incoming_element = incoming.create_as(Element, current_element.id)
    incoming_common = incoming.create_as(Diagram, current_common.id)
    incoming_common.element = incoming_element

    remove_ref, other_ref = sorted(compare(current, incoming), key=lambda c: c.op)

    assert remove_ref.op == "remove"
    assert remove_ref.element_id == incoming_element.id
    assert remove_ref.property_name == "ownedDiagram"
    assert remove_ref.property_ref == current_diagram.id

    assert other_ref.op == "update"
    assert other_ref.element_id == current_diagram.id
    assert other_ref.property_name == "element"
    assert other_ref.property_ref is None


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


def test_style_sheet_with_different_ids(current, incoming):
    current.create(StyleSheet)
    incoming.create(StyleSheet)

    changes = set(compare(current, incoming))

    assert not changes


def test_style_sheet_comparison(current, incoming):
    current_style_sheet = current.create(StyleSheet)
    incoming_style_sheet = incoming.create(StyleSheet)
    incoming_style_sheet.styleSheet = "foo {}"

    change = next(compare(current, incoming))

    assert change.op == "update"
    assert change.element_id == current_style_sheet.id
    assert change.property_name == "styleSheet"
    assert change.property_value == "foo {}"
