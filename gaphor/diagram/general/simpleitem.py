"""Trivial drawing aids (box, line, ellipse)."""

from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.shapes import Box as BoxShape
from gaphor.diagram.shapes import CssNode, Text, draw_border, draw_ellipse


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id, shape_middle=text_label(self))
        self._handles[0].connectable = False
        self._handles[-1].connectable = False
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
