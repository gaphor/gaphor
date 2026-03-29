"""Unit tests for simple items."""

from gaphor.diagram.general.simpleitem import Box, Ellipse, Line, LineEndStyle


def test_line(diagram):
    line = diagram.create(Line)

    assert line
    assert line.head_end == LineEndStyle.none
    assert line.tail_end == LineEndStyle.none


def test_box(diagram):
    assert diagram.create(Box)


def test_ellipse(diagram):
    assert diagram.create(Ellipse)
