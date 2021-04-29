"""Unit tests for simple items."""

from gaphor.diagram.general.simpleitem import Box, Ellipse, Line


def test_line(case):
    case.diagram.create(Line)


def test_box(case):
    case.diagram.create(Box)


def test_ellipse(case):
    case.diagram.create(Ellipse)
