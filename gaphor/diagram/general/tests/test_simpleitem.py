"""Unit tests for simple items."""

import cairo
import pytest

from gaphor.core.modeling import DrawContext
from gaphor.diagram.general.simpleitem import (
    Box,
    Ellipse,
    Line,
    LineEndStyle,
    _draw_head,
    _draw_tail,
)


def test_line(diagram):
    line = diagram.create(Line)

    assert line
    assert line.head_end == LineEndStyle.none
    assert line.tail_end == LineEndStyle.none


def test_box(diagram):
    assert diagram.create(Box)


def test_ellipse(diagram):
    assert diagram.create(Ellipse)


def _end_shape_corners(draw, style):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cr = cairo.Context(surface)
    context = DrawContext(
        cairo=cr,
        style={"color": (0, 0, 0, 1)},
        selected=False,
        focused=False,
        hovered=False,
        dropzone=False,
    )
    cr.move_to(100, 0)
    draw(context, style)

    corners = 0
    for op, _points in cr.copy_path():
        if op == cairo.PATH_MOVE_TO:
            corners = 1
        elif op == cairo.PATH_LINE_TO:
            corners += 1
        elif op == cairo.PATH_CLOSE_PATH:
            return corners
    return None


@pytest.mark.parametrize("draw", [_draw_head, _draw_tail])
@pytest.mark.parametrize(
    "style, corners", [(LineEndStyle.triangle, 3), (LineEndStyle.diamond, 4)]
)
def test_line_end_shape(draw, style, corners):
    assert _end_shape_corners(draw, style) == corners
