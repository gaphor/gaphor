"""
Generalization -- 
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram.diagramline import DiagramLine


class GeneralizationItem(DiagramLine):
    __uml__ = uml2.Generalization
    __relationship__ = 'general', None, 'specific', 'generalization'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.close_path()
        cr.stroke()
        cr.move_to(15, 0)

# vim:sw=4:et:ai
