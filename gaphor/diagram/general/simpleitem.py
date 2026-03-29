"""Trivial drawing aids (box, line, ellipse)."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.shapes import Box as BoxShape
from gaphor.diagram.shapes import CssNode, Text, draw_border, draw_ellipse, stroke


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id, shape_middle=text_label(self))
        self.watch("label")

    label: attribute[str] = attribute("label", str)


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


def text_label(item: Box | Ellipse):
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
