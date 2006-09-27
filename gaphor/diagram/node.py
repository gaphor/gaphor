"""
Node item.
"""

from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem

class NodeItem(ClassifierItem):

    __uml__ = UML.Node

    DEPTH = 10

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self.height = 50
        self.width = 120

    def draw_compartment(self, context):
        cr = context.cairo
        cr.save()
        super(NodeItem, self).draw_compartment(context)
        cr.restore()

        d = self.DEPTH
        w = self.width
        h = self.height

        cr.move_to(0, 0)
        cr.line_to(d, -d)
        cr.line_to(w + d, -d)
        cr.line_to(w + d, h - d)
        cr.line_to(w, h)
        cr.move_to(w, 0)
        cr.line_to(w + d, -d)

        cr.stroke()


# vim:sw=4:et
