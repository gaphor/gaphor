import pytest

from gaphor import UML
from gaphor.core.modeling import Comment
from gaphor.diagram.tests.fixtures import connect
from gaphor.plugins.autolayout.pydot import AutoLayout, parse_edge_pos
from gaphor.UML.diagramitems import (
    AssociationItem,
    ClassItem,
    CommentItem,
    CommentLineItem,
    GeneralizationItem,
    PackageItem,
)


def test_layout_diagram(diagram, create, event_manager):
    superclass = create(ClassItem, UML.Class)
    subclass = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem, UML.Generalization)
    connect(gen, gen.tail, superclass)
    connect(gen, gen.head, subclass)

    auto_layout = AutoLayout(event_manager, None)
    auto_layout.layout(diagram)

    assert gen.head.pos != (0, 0)
    assert gen.tail.pos != (0, 0)


def test_layout_with_association(diagram, create, event_manager):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    auto_layout = AutoLayout(event_manager, None)
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

    auto_layout = AutoLayout(event_manager, None)
    auto_layout.layout(diagram)


def test_layout_with_nested(diagram, create, event_manager):
    p = create(PackageItem, UML.Package)
    c1 = create(ClassItem, UML.Class)
    c1.subject.package = p.subject
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)
    connect(a, a.head, c1)
    connect(a, a.tail, c2)

    auto_layout = AutoLayout(event_manager, None)
    auto_layout.layout(diagram)


def test_parse_pos():
    points = parse_edge_pos('"1.0,2.0 3.0,4 5.0,6.0 7,8.0"')

    assert points == [(1.0, 2.0), (7.0, 8.0)]


def test_parse_pos_invalid_number_of_points():
    with pytest.raises(IndexError):
        parse_edge_pos('"1.0,2.0 3.0,4 5.0,6.0"')
