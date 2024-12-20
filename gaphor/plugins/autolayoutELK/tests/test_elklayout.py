import json

from gaphor import UML
from gaphor.diagram.tests.fixtures import connect
from gaphor.plugins.autolayoutELK.autolayoutelk import (
    AutoLayoutELK,
    _parse_edge_pos,
    _strip_quotes,
)
from gaphor.UML.diagramitems import (
    ActionItem,
    AssociationItem,
    ClassItem,
    ForkNodeItem,
    GeneralizationItem,
    InputPinItem,
    ObjectFlowItem,
    PackageItem,
)
from gaphor.UML.general import CommentItem, CommentLineItem


def test_layout_diagram(diagram, create):
    superclass = create(ClassItem, UML.Class)
    subclass = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem, UML.Generalization)
    connect(gen, gen.tail, superclass)
    connect(gen, gen.head, subclass)

    auto_layout = AutoLayoutELK()
    auto_layout.layout(diagram)

    assert gen.head.pos != (0, 0)
    assert gen.tail.pos != (0, 0)


def test_layout_with_association(diagram, create, event_manager):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    auto_layout = AutoLayoutELK(event_manager)
    auto_layout.layout(diagram)


def test_layout_with_comment(diagram, create, event_manager):
    """Failure due to comment line connecting to an edge.

    How to treat? May need to link to a node (such as the edge label?,
    e.g., is source/target is an edge then connect to the associated label)"""
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    comment = create(CommentItem, UML.Comment)
    comment_line = create(CommentLineItem)
    connect(comment_line, comment_line.head, comment)
    connect(comment_line, comment_line.tail, a)

    auto_layout = AutoLayoutELK(event_manager)
    auto_layout.layout(diagram)


def test_layout_with_nested(diagram, create, event_manager):
    p = create(PackageItem, UML.Package)
    c1 = create(ClassItem, UML.Class)
    p.children = c1
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    auto_layout = AutoLayoutELK(event_manager)
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

    auto_layout = AutoLayoutELK(event_manager)
    auto_layout.layout(diagram)

    assert pin.parent is action


def test_layout_fork_node_item(diagram, create, event_manager):
    create(ForkNodeItem, UML.ForkNode)

    auto_layout = AutoLayoutELK(event_manager)
    auto_layout.layout(diagram)


def test_parse_pos():
    json_test_string = '{"sections": [{"startPoint": {"x": 1.0, "y": 2.0}, "endPoint": {"x": 3.0, "y": 4.0}}]}'
    section_list = json.loads(json_test_string)
    relative_location = [0.0, 0.0]
    points = _parse_edge_pos(section_list["sections"], relative_location, False)

    assert points == [(1.0, 2.0), (3.0, 4.0)]


def test_strip_line_endings():
    assert _strip_quotes("\\\n807.5") == "807.5"
    assert _strip_quotes("\\\r\n807.5") == "807.5"
    assert _strip_quotes('\\\r\n"807.5"') == "807.5"
