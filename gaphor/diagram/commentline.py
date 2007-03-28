"""
CommentLine -- A line that connects a comment to another model element.

"""

import gobject
from gaphor import UML

from diagramline import DiagramLine

class CommentLineItem(DiagramLine):

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

    def save (self, save_func):
        DiagramLine.save(self, save_func)
    
    def load (self, name, value):
        DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)

    def on_notify_comment_parent(self, comment, pspec):
        if not comment.parent and self.parent:
            self.parent.remove(self)
            
    def draw(self, context):
        context.cairo.set_dash((7.0, 5.0), 0)
        DiagramLine.draw(self, context)

# vim: sw=4:et:ai
