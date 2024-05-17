"""Trivial drawing aids (box, line, ellipse)."""

from gaphor.core.modeling.diagram import StyledItem
from gaphor.diagram.presentation import (
    ElementPresentation,
    LinePresentation,
    PresentationStyle,
)
from gaphor.diagram.shapes import Box as BoxShape
from gaphor.diagram.shapes import draw_border, draw_ellipse


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self._handles[0].connectable = False
        self._handles[-1].connectable = False

        self.presentation_style = PresentationStyle(
            self.diagram.styleSheet, StyledItem(self).name()
        )


class Box(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self.shape = BoxShape(
            draw=draw_border,
        )

        self.presentation_style = PresentationStyle(
            self.diagram.styleSheet, StyledItem(self).name()
        )


class Ellipse(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self.shape = BoxShape(
            draw=draw_ellipse,
        )

        self.presentation_style = PresentationStyle(
            self.diagram.styleSheet, StyledItem(self).name()
        )
