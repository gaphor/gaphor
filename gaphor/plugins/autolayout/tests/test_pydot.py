import pytest

from gaphor import UML
from gaphor.core.modeling import Comment
from gaphor.diagram.tests.fixtures import connect
from gaphor.plugins.autolayout.pydot import AutoLayout, parse_edge_pos, strip_quotes
from gaphor.UML.diagramitems import (
    ActionItem,
    AssociationItem,
    ClassItem,
    CommentItem,
    CommentLineItem,
    ForkNodeItem,
    GeneralizationItem,
    InputPinItem,
    ObjectFlowItem,
    PackageItem,
)


def test_layout_diagram(diagram, create):
    superclass = create(ClassItem, UML.Class)
    subclass = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem, UML.Generalization)
    connect(gen, gen.tail, superclass)
    connect(gen, gen.head, subclass)

    auto_layout = AutoLayout()
    auto_layout.layout(diagram)

    assert gen.head.pos != (0, 0)
    assert gen.tail.pos != (0, 0)


def test_layout_with_association(diagram, create, event_manager):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    auto_layout = AutoLayout(event_manager)
    auto_layout.layout(diagram)


def test_layout_with_comment(diagram, create, event_manager):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    comment = create(CommentItem, Comment)
    comment_line = create(CommentLineItem)
    connect(comment_line, comment_line.head, comment)
    connect(comment_line, comment_line.tail, a)

    auto_layout = AutoLayout(event_manager)
    auto_layout.layout(diagram)


def test_layout_with_nested(diagram, create, event_manager):
    p = create(PackageItem, UML.Package)
    c1 = create(ClassItem, UML.Class)
    p.children = c1
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    auto_layout = AutoLayout(event_manager)
    auto_layout.layout(diagram)

    assert c1.matrix[4] < p.width
    assert c1.matrix[5] < p.height


def test_layout_with_attached_item(diagram, create, event_manager):
    action = create(ActionItem, UML.Action)
    pin = create(InputPinItem, UML.InputPin)
    connect(pin, pin.handles()[0], action)

    action2 = create(ActionItem, UML.Action)
    object_flow = create(ObjectFlowItem, UML.ObjectFlow)
    connect(object_flow, object_flow.head, pin)
    connect(object_flow, object_flow.tail, action2)

    auto_layout = AutoLayout(event_manager)
    auto_layout.layout(diagram)

    assert pin.parent is action


def test_layout_fork_node_item(diagram, create, event_manager):
    create(ForkNodeItem, UML.ForkNode)

    auto_layout = AutoLayout(event_manager)
    auto_layout.layout(diagram)


def test_parse_pos():
    points = parse_edge_pos('"1.0,2.0 3.0,4 5.0,6.0 7,8.0"', 10, True)

    assert points == [(7.0, 2.0), (1.0, 8.0)]


def test_parse_pos_invalid_number_of_points():
    with pytest.raises(IndexError):
        parse_edge_pos('"1.0,2.0 3.0,4 5.0,6.0"', 10, True)


def test_strip_line_endings():
    assert strip_quotes("\\\n807.5") == "807.5"
    assert strip_quotes("\\\r\n807.5") == "807.5"
    assert strip_quotes('\\\r\n"807.5"') == "807.5"
