"""
Implementation of interface.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram.diagramline import DiagramLine


class ImplementationItem(DiagramLine):
    __uml__ = uml2.Implementation

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        self._solid = False

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        if not self._solid:
            cr.set_dash((), 0)
            cr.line_to(15, -10)
            cr.line_to(15, 10)
            cr.close_path()
            cr.stroke()
            cr.move_to(15, 0)

    def draw(self, context):
        if not self._solid:
            context.cairo.set_dash((7.0, 5.0), 0)
        super(ImplementationItem, self).draw(context)

# vim:sw=4
