"""Trivial drawing aids (box, line, ellipse)."""

from gaphas.item import NW
from gaphas.util import path_ellipse

from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.shapes import stroke


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self._handles[0].connectable = False
        self._handles[-1].connectable = False


class Box(ElementPresentation):
    """A Box has 4 handles (for a start)::

    NW +---+ NE SW +---+ SE
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)

    def draw(self, context):
        cr = context.cairo
        nw = self._handles[NW]
        cr.rectangle(nw.pos.x, nw.pos.y, self.width, self.height)
        stroke(context)


class Ellipse(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)

    def draw(self, context):
        cr = context.cairo

        x, y = self.handles()[0].pos
        rx = self.width / 2.0
        ry = self.height / 2.0

        cr.move_to(x + self.width, y + ry)
        path_ellipse(cr, x + rx, y + ry, self.width, self.height)
        stroke(context)
