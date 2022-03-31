"""Unit tests for simple items."""

from gaphor.diagram.general.simpleitem import Box, Ellipse, Line


def test_line(diagram):
    assert diagram.create(Line)


def test_box(diagram):
    assert diagram.create(Box)


def test_ellipse(diagram):
    assert diagram.create(Ellipse)
