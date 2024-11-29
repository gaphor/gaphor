"""Trivial drawing aids (box, line, ellipse)."""

from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.shapes import Box as BoxShape
from gaphor.diagram.shapes import draw_border, draw_ellipse


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self._handles[0].connectable = False
        self._handles[-1].connectable = False


class Box(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self.shape = BoxShape(
            draw=draw_border,
        )


class Ellipse(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self.shape = BoxShape(
            draw=draw_ellipse,
        )
