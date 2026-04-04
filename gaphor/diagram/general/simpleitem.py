"""Trivial drawing aids (box, line, ellipse)."""

import enum

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.properties import attribute, enumeration
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.shapes import Box as BoxShape
from gaphor.diagram.shapes import CssNode, Text, draw_border, draw_ellipse, stroke


class LineEndStyle(enum.StrEnum):
    none = "none"
    arrow = "arrow"
    triangle = "triangle"
    diamond = "diamond"


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id, shape_middle=text_label(self))
        self.watch("label")
        self.watch("head_end", lambda *_: self.request_update())
        self.watch("tail_end", lambda *_: self.request_update())

    label: attribute[str] = attribute("label", str)
    head_end = enumeration("head_end", LineEndStyle, LineEndStyle.none)
    tail_end = enumeration("tail_end", LineEndStyle, LineEndStyle.none)

    def draw_head(self, context):
        _draw_head(context, self.head_end)

    def draw_tail(self, context):
        _draw_tail(context, self.tail_end)


class Box(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram=diagram,
            id=id,
            shape=BoxShape(
                text_label(self),
                draw=draw_border,
            ),
        )
        self.watch("label")

    label: attribute[str] = attribute("label", str)


class Diamond(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram=diagram,
            id=id,
            shape=BoxShape(
                text_label(self),
                draw=draw_diamond,
            ),
        )
        self.watch("label")

    label: attribute[str] = attribute("label", str)


class Ellipse(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram=diagram,
            id=id,
            shape=BoxShape(
                text_label(self),
                draw=draw_ellipse,
            ),
        )
        self.watch("label")

    label: attribute[str] = attribute("label", str)


def text_label(item: Line | Box | Ellipse):
    """An item's `label` field."""
    return CssNode(
        "label",
        None,
        Text(text=lambda: item.label or ""),
    )


def draw_diamond(_box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    x, y, width, height = bounding_box
    cx = width / 2
    cy = height / 2

    cr.set_dash(context.style.get("dash-style", ()), 0)
    cr.move_to(x + cx, y)
    cr.line_to(x + width, y + cy)
    cr.line_to(x + cx, y + height)
    cr.line_to(x, y + cy)
    cr.close_path()
    stroke(context, fill=True)


def _draw_head(context: DrawContext, style: LineEndStyle):
    cr = context.cairo
    if style == LineEndStyle.arrow:
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
        cr.move_to(0, 0)
    elif style == LineEndStyle.triangle:
        cr.move_to(20, 0)
        cr.line_to(10, -6)
        cr.line_to(0, 0)
        cr.line_to(10, 6)
        cr.close_path()
    elif style == LineEndStyle.diamond:
        cr.move_to(20, -12)
        cr.line_to(20, 12)
        cr.line_to(0, 0)
        cr.close_path()
        cr.move_to(20, 0)
    else:
        cr.move_to(0, 0)


def _draw_tail(context: DrawContext, style: LineEndStyle):
    cr = context.cairo
    if style == LineEndStyle.arrow:
        cr.line_to(0, 0)
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
    elif style == LineEndStyle.triangle:
        cr.line_to(20, 0)
        stroke(context, fill=True)
        cr.move_to(20, 0)
        cr.line_to(10, -6)
        cr.line_to(0, 0)
        cr.line_to(10, 6)
        cr.close_path()
    elif style == LineEndStyle.diamond:
        cr.line_to(20, 0)
        stroke(context, fill=True)
        cr.move_to(20, -12)
        cr.line_to(0, 0)
        cr.line_to(20, 12)
        cr.close_path()
    else:
        cr.line_to(0, 0)
