"""
Node item.
"""

import diacanvas
from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem

class NodeItem(ClassifierItem):

    __uml__ = UML.Node

    DEPTH = 10

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=120)

        for attr in ('_back', '_diag_line'):
            shape = diacanvas.shape.Path()
            shape.set_line_width(2.0)
            setattr(self, attr, shape)

        self._shapes.update((self._back, self._diag_line))


    def on_update(self, affine):
        ClassifierItem.on_update(self, affine)

        d = self.DEPTH
        w = self.width
        h = self.height

        self._back.line(((0, 0), (d, -d), (w + d, -d), (w + d, h - d), (w, h)))
        self._diag_line.line(((w, 0), (w + d, -d)))

        x0, y0, x1, y1 = self.bounds
        self.set_bounds((x0, y0 - d, x1 + d, y1))

# vim:sw=4:et
