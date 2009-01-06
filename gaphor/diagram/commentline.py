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
        if self.head.connected_to and self.tail.connected_to:
            query = (self.head.connected_to, self)
            adapter = component.queryMultiAdapter(query, IConnect)
            adapter.disconnect(self.head)
        super(CommentLineItem, self).unlink()


    def draw(self, context):
        context.cairo.set_dash((7.0, 5.0), 0)
        DiagramLine.draw(self, context)


# vim: sw=4:et:ai
