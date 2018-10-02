"""
Use case inclusion relationship.
"""

from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine

class IncludeItem(DiagramLine):
    """
    Use case inclusion relationship.
    """

    __uml__ = UML.Include
    __stereotype__ = 'include'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

    def draw_head(self, context):
        cr = context.cairo
        cr.set_dash((), 0)
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
        cr.stroke()
        cr.move_to(0, 0)

    def draw(self, context):
        context.cairo.set_dash((7.0, 5.0), 0)
        super(IncludeItem, self).draw(context)


# vim:sw=4:et
