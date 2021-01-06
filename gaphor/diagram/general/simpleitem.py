"""Trivial drawing aids (box, line, ellipse)."""

import ast

from gaphas.item import NW, Element
from gaphas.util import path_ellipse

from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import stroke


class Line(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram=diagram, id=id)
        self._handles[0].connectable = False
        self._handles[-1].connectable = False


class Box(Element, Presentation):
    """A Box has 4 handles (for a start)::

    NW +---+ NE SW +---+ SE
    """

    def __init__(self, diagram, id=None):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id)  # type: ignore[call-arg]

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("width", self.width)
        save_func("height", self.height)

    def load(self, name, value):
        if name == "matrix":
            self.matrix.set(*ast.literal_eval(value))
        elif name == "width":
            self.width = ast.literal_eval(value)
        elif name == "height":
            self.height = ast.literal_eval(value)

    def postload(self):
        pass

    def pre_update(self, context):
        pass

    def post_update(self, context):
        pass

    def draw(self, context):
        cr = context.cairo
        nw = self._handles[NW]
        cr.rectangle(nw.pos.x, nw.pos.y, self.width, self.height)
        stroke(context)


class Ellipse(Element, Presentation):
    """"""

    def __init__(self, diagram, id=None):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id)  # type: ignore[call-arg]

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("width", self.width)
        save_func("height", self.height)

    def load(self, name, value):
        if name == "matrix":
            self.matrix.set(*ast.literal_eval(value))
        elif name == "width":
            self.width = ast.literal_eval(value)
        elif name == "height":
            self.height = ast.literal_eval(value)

    def postload(self):
        pass

    def pre_update(self, context):
        pass

    def post_update(self, context):
        pass

    def draw(self, context):
        cr = context.cairo

        rx = self.width / 2.0
        ry = self.height / 2.0

        cr.move_to(self.width, ry)
        path_ellipse(cr, rx, ry, self.width, self.height)
        stroke(context)
