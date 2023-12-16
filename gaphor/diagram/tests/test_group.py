from gaphor.core.modeling import Diagram, Element, ElementFactory
from gaphor.diagram.group import can_group, change_owner, group, ungroup


def test_group_diagram(element_factory):
    diagram = element_factory.create(Diagram)
    parent = element_factory.create(Element)

    assert group(parent, diagram)

    assert diagram.element is parent


def test_ungroup_diagram(element_factory):
    diagram = element_factory.create(Diagram)
    parent = element_factory.create(Element)
    diagram.element = parent

    assert ungroup(parent, diagram)

    assert diagram.element is None


def test_ungroup_no_parent(element_factory):
    element = element_factory.create(Element)

    assert ungroup(None, element)


def test_do_not_ungroup_diagram_from_wrong_parent(element_factory):
    diagram = element_factory.create(Diagram)
    parent = element_factory.create(Element)
    wrong_parent = element_factory.create(Element)
    diagram.element = parent

    assert not ungroup(wrong_parent, diagram)

    assert diagram.element is parent


def test_can_group_with_type(element_factory):
    parent = element_factory.create(Element)

    assert can_group(parent, Diagram)


def test_can_group_with_instance(element_factory):
    diagram = element_factory.create(Diagram)
    parent = element_factory.create(Element)

    assert can_group(parent, diagram)


def test_cannot_change_owner_from_different_models(element_factory):
    other_element_factory = ElementFactory()
    diagram = element_factory.create(Diagram)
    parent = other_element_factory.create(Element)

    assert not change_owner(parent, diagram)


def test_change_owner_to_root(element_factory):
    diagram = element_factory.create(Diagram)
    parent = element_factory.create(Element)
    change_owner(parent, diagram)

    assert change_owner(None, diagram)
    assert diagram.owner is None
