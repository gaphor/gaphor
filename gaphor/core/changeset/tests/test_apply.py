import pytest

from gaphor.core.changeset.apply import applicable, apply_change
from gaphor.core.modeling import (
    Diagram,
    Element,
    ElementChange,
    RefChange,
    ValueChange,
)
from gaphor.UML import Class, Property


def test_create_element(element_factory, modeling_language):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "12234"
    change.element_name = "Diagram"

    apply_change(change, element_factory, modeling_language)

    diagram = next(element_factory.select(Diagram))

    assert diagram
    assert element_factory.lookup(change.element_id)
    assert change.applied


def test_create_presentation(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Box"
    change.diagram_id = diagram.id

    apply_change(change, element_factory, modeling_language)

    assert element_factory.lookup(change.element_id)
    assert change.applied


def test_create_presentation_without_diagram(element_factory, modeling_language):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "12234"
    change.element_name = "Box"

    with pytest.raises(TypeError):
        apply_change(change, element_factory, modeling_language)


def test_remove_element(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "remove"
    change.element_id = diagram.id
    change.element_name = "Diagram"

    apply_change(change, element_factory, modeling_language)

    assert diagram not in element_factory
    assert change.applied


def test_update_str_value(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = diagram.id
    change.property_name = "name"
    change.property_value = "new value"

    apply_change(change, element_factory, modeling_language)

    assert diagram.name == "new value"
    assert change.applied


def test_update_int_value(element_factory, modeling_language):
    klass = element_factory.create(Class)
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = klass.id
    change.property_name = "isAbstract"
    change.property_value = "1"

    apply_change(change, element_factory, modeling_language)

    assert klass.isAbstract == 1
    assert change.applied


def test_update_str_default_value(element_factory, modeling_language):
    diagram = element_factory.create(Diagram)
    diagram.name = "old name"
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = diagram.id
    change.property_name = "name"

    apply_change(change, element_factory, modeling_language)

    assert not diagram.name
    assert change.applied


def test_update_int_default_value(element_factory, modeling_language):
    klass = element_factory.create(Class)
    klass.isAbstract = 1
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = klass.id
    change.property_name = "isAbstract"

    apply_change(change, element_factory, modeling_language)

    assert not klass.isAbstract
    assert change.applied


def test_update_enumeration_default_value(element_factory, modeling_language):
    property = element_factory.create(Property)
    property.aggregation = "shared"
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = property.id
    change.property_name = "aggregation"

    apply_change(change, element_factory, modeling_language)

    assert property.aggregation == "none"
    assert change.applied


def test_add_relation(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)
    change: RefChange = element_factory.create(RefChange)
    change.op = "add"
    change.element_id = diagram.id
    change.property_name = "element"
    change.property_ref = element.id

    apply_change(change, element_factory, modeling_language)

    assert diagram.element is element
    assert change.applied


def test_remove_single_relation(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)
    diagram.element = element

    change: RefChange = element_factory.create(RefChange)
    change.op = "remove"
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
    change.op = "remove"
    change.element_id = element.id
    change.property_name = "ownedDiagram"
    change.property_ref = diagram.id

    apply_change(change, element_factory, modeling_language)

    assert diagram.element is None


def test_apply_opposite_relation(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)

    change: RefChange = element_factory.create(RefChange)
    change.op = "add"
    change.element_id = element.id
    change.property_name = "ownedDiagram"
    change.property_ref = diagram.id

    other: RefChange = element_factory.create(RefChange)
    other.op = "update"
    other.element_id = diagram.id
    other.property_name = "element"
    other.property_ref = element.id

    apply_change(change, element_factory, modeling_language)

    assert change.applied
    assert other.applied


def test_element_change_applicable(element_factory):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Presentation"

    assert applicable(change, element_factory)


def test_element_change_not_applicable(element_factory):
    element_factory.create_as(Element, id="1234")
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Presentation"

    assert not applicable(change, element_factory)


def test_element_change_with_diagram_applicable(element_factory):
    diagram = element_factory.create(Diagram)
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Presentation"
    change.diagram_id = diagram.id

    assert applicable(change, element_factory)


def test_element_change_without_diagram_not_applicable(element_factory):
    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Presentation"
    change.diagram_id = "does-not-exist"

    assert not applicable(change, element_factory)


def test_update_value_applicable(element_factory):
    diagram = element_factory.create(Diagram)
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = diagram.id
    change.property_name = "name"
    change.property_value = "new value"

    assert applicable(change, element_factory)


def test_update_value_not_applicable(element_factory):
    diagram = element_factory.create(Diagram)
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = diagram.id
    change.property_name = "name"
    change.property_value = "new value"
    diagram.name = "new value"

    assert not applicable(change, element_factory)


def test_update_value_without_element_not_applicable(element_factory):
    change: ValueChange = element_factory.create(ValueChange)
    change.element_id = "1234"
    change.property_name = "name"
    change.property_value = "new value"

    assert not applicable(change, element_factory)


def test_add_relation_applicable(element_factory, modeling_language):
    element = element_factory.create(Element)
    diagram = element_factory.create(Diagram)
    change: RefChange = element_factory.create(RefChange)
    change.op = "add"
    change.element_id = diagram.id
    change.property_name = "element"
    change.property_ref = element.id

    assert applicable(change, element_factory)
