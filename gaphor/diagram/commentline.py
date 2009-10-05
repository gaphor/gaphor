"""
CommentLine -- A line that connects a comment to another model element.

"""

import gobject
from zope import component
from gaphor import UML

from diagramline import DiagramLine
from interfaces import IConnect


class CommentLineItem(DiagramLine):

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)


    def save (self, save_func):
        DiagramLine.save(self, save_func)
    

    def load (self, name, value):
        DiagramLine.load(self, name, value)


    def postload(self):
        DiagramLine.postload(self)


    def unlink(self):
        canvas = self.canvas
        hct = canvas.get_connected_to(self, self.head)
        tct = canvas.get_connected_to(self, self.tail)
        if hct and tct:
            query = (hct[0], self)
            adapter = component.queryMultiAdapter(query, IConnect)
            adapter.disconnect(self.head)
        super(CommentLineItem, self).unlink()


    def draw(self, context):
        context.cairo.set_dash((7.0, 5.0), 0)
        DiagramLine.draw(self, context)


# vim: sw=4:et:ai
