"""Test general item connectors (Box, Ellipse, Line)."""

from gaphor.diagram.general import Box, Ellipse, Line
from gaphor.diagram.tests.fixtures import allow, connect, disconnect


def test_allow_line_to_box(create):
    box = create(Box)
    line = create(Line)

    allowed = allow(line, line.head, box)
    assert allowed


def test_connect_line_head_to_box(create):
    box = create(Box)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.head, box)

    cinfo = diagram.connections.get_connection(line.head)
    assert cinfo.connected is box
    assert cinfo.item is line


def test_connect_line_tail_to_box(create):
    box = create(Box)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.tail, box)

    cinfo = diagram.connections.get_connection(line.tail)
    assert cinfo.connected is box
    assert cinfo.item is line


def test_disconnect_line_from_box(create):
    box = create(Box)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.head, box)
    assert diagram.connections.get_connection(line.head) is not None

    disconnect(line, line.head)
    assert diagram.connections.get_connection(line.head) is None


def test_connect_both_ends_to_boxes(create):
    box1 = create(Box)
    box2 = create(Box)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.head, box1)
    connect(line, line.tail, box2)

    head_cinfo = diagram.connections.get_connection(line.head)
    tail_cinfo = diagram.connections.get_connection(line.tail)

    assert head_cinfo.connected is box1
    assert tail_cinfo.connected is box2
    assert head_cinfo.item is line
    assert tail_cinfo.item is line


def test_allow_line_to_ellipse(create):
    ellipse = create(Ellipse)
    line = create(Line)

    allowed = allow(line, line.head, ellipse)
    assert allowed


def test_connect_line_head_to_ellipse(create):
    ellipse = create(Ellipse)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.head, ellipse)

    cinfo = diagram.connections.get_connection(line.head)
    assert cinfo.connected is ellipse
    assert cinfo.item is line


def test_connect_line_tail_to_ellipse(create):
    ellipse = create(Ellipse)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.tail, ellipse)

    cinfo = diagram.connections.get_connection(line.tail)
    assert cinfo.connected is ellipse
    assert cinfo.item is line


def test_disconnect_line_from_ellipse(create):
    ellipse = create(Ellipse)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.head, ellipse)
    assert diagram.connections.get_connection(line.head) is not None

    disconnect(line, line.head)
    assert diagram.connections.get_connection(line.head) is None


def test_connect_line_between_box_and_ellipse(create):
    box = create(Box)
    ellipse = create(Ellipse)
    line = create(Line)
    diagram = line.diagram

    connect(line, line.head, box)
    connect(line, line.tail, ellipse)

    head_cinfo = diagram.connections.get_connection(line.head)
    tail_cinfo = diagram.connections.get_connection(line.tail)

    assert head_cinfo.connected is box
    assert tail_cinfo.connected is ellipse
