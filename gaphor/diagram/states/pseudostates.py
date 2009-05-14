"""
Pseudostate diagram items.

See also gaphor.diagram.states package description.
"""

from gaphor import UML
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP
from gaphas.util import path_ellipse, text_center

from gaphor.diagram.states import VertexItem


class InitialPseudostateItem(VertexItem):
    """
    Initial pseudostate diagram item.
    """
    __uml__   = UML.Pseudostate
    __style__ = {
        'min-size':   (20, 20),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
        'name-padding': (2, 2, 2, 2),
        'name-outside': True,
    }

    RADIUS = 10
    def __init__(self, id=None):
        super(InitialPseudostateItem, self).__init__(id)
        for h in self.handles():
            h.movable = False


    def draw(self, context):
        """
        Draw intial pseudostate symbol.
        """
        super(InitialPseudostateItem, self).draw(context)
        cr = context.cairo
        r = self.RADIUS
        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.fill()


class HistoryPseudostateItem(VertexItem):
    """
    History pseudostate diagram item.
    """
    __uml__   = UML.Pseudostate
    __style__ = {
        'min-size':   (30, 30),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
        'name-padding': (2, 2, 2, 2),
        'name-outside': True,
    }

    RADIUS = 15
    def __init__(self, id=None):
        super(HistoryPseudostateItem, self).__init__(id)
        for h in self.handles():
            h.movable = False


    def draw(self, context):
        """
        Draw intial pseudostate symbol.
        """
        super(HistoryPseudostateItem, self).draw(context)
        cr = context.cairo
        r = self.RADIUS
        d = r * 2
        path_ellipse(cr, r, r, d, d)
        #cr.set_line_width(1)
        cr.stroke()
        text_center(cr, r, r, "H")

# vim:sw=4:et
