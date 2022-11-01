import pytest

from gaphor.core.changeset.apply import ADD, REMOVE, apply_change
from gaphor.core.modeling import (
    Diagram,
    Element,
    ElementChange,
    Presentation,
    RefChange,
    ValueChange,
)


def test_create_element(element_factory, modeling_language):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = ADD
    change.element_id = "12234"
    change.element_name = "Diagram"

    apply_change(change, element_factory, modeling_language)

    diagram = next(element_factory.select(Diagram))

    assert diagram


def test_create_presentation(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    change: ElementChange = element_factory.create(ElementChange)
    change.op = ADD
    change.element_id = "12234"
    change.element_name = "Presentation"

    apply_change(change, element_factory, modeling_language, diagram=diagram)

    presentation = next(element_factory.select(Presentation))

    assert presentation


def test_create_presentation_without_diagram(element_factory, modeling_language):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = ADD
    change.element_id = "12234"
    change.element_name = "Presentation"

    with pytest.raises(TypeError):
        apply_change(change, element_factory, modeling_language)


def test_remove_element(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    change: ElementChange = element_factory.create(ElementChange)
    change.op = REMOVE
    change.element_id = diagram.id
    change.element_name = "Diagram"

    apply_change(change, element_factory, modeling_language)

    assert diagram not in element_factory


def test_update_value(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = diagram.id
    change.property_name = "name"
    change.property_value = "new value"

    apply_change(change, element_factory, modeling_language)

    assert diagram.name == "new value"


def test_add_relation(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)
    change: RefChange = element_factory.create(RefChange)
    change.op = ADD
    change.element_id = diagram.id
    change.property_name = "element"
    change.property_ref = element.id

    apply_change(change, element_factory, modeling_language)

    assert diagram.element is element


def test_remove_single_relation(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)
    diagram.element = element

    change: RefChange = element_factory.create(RefChange)
    change.op = REMOVE
    change.element_id = diagram.id
    change.property_name = "element"
    change.property_ref = element.id

    apply_change(change, element_factory, modeling_language)

    assert diagram.element is None


def test_remove_many_relation(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)
    diagram.element = element

    change: RefChange = element_factory.create(RefChange)
    change.op = REMOVE
    change.element_id = element.id
    change.property_name = "ownedDiagram"
    change.property_ref = diagram.id

    apply_change(change, element_factory, modeling_language)

    assert diagram.element is None
