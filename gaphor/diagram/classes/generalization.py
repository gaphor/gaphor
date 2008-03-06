"""
Generalization -- 
"""

import gobject

from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine

class GeneralizationItem(DiagramLine):

    __uml__ = UML.Generalization
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
