"""
Final state diagram item.
"""

from gaphor import UML
from gaphor.diagram.style import ALIGN_RIGHT, ALIGN_BOTTOM
from gaphas.util import path_ellipse

from gaphor.diagram.states.state import VertexItem


class FinalStateItem(VertexItem):
    __uml__ = UML.FinalState
    __style__ = {
        "min-size": (30, 30),
        "name-align": (ALIGN_RIGHT, ALIGN_BOTTOM),
        "name-padding": (2, 2, 2, 2),
        "name-outside": True,
    }

    RADIUS_1 = 10
    RADIUS_2 = 15

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        for h in self.handles():
            h.movable = False

    def draw(self, context):
        """
        Draw final state symbol.
        """
        cr = context.cairo
        r = self.RADIUS_2 + 1
        d = self.RADIUS_1 * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.fill()

        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.set_line_width(2)
        cr.stroke()

        super(FinalStateItem, self).draw(context)


# vim:sw=4:et
