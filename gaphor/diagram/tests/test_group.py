from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.group import can_group, group, ungroup


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
