# vim:sw=4:et
'''
CommentLine -- A line that connects a comment to another model element.

TODO: Why do we lose the __id property when we do a get_property after a model
has been loaded. It works okay when creating new items.
'''

import gobject
from gaphor import UML

from diagramline import DiagramLine

class CommentLineItem(DiagramLine):

    def __init__(self, id=None):
        #diacanvas.CanvasLine.__init__(self)
        DiagramLine.__init__(self, id)
        self.__notify_id = None

    #id = property(lambda self: self._id, doc='Id')

    def save (self, save_func):
        DiagramLine.save(self, save_func)
    
    def load (self, name, value):
        DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)

    def on_notify_comment_parent(self, comment, pspec):
        if not comment.parent and self.parent:
            self.parent.remove(self)
            

# vim: sw=4:et:ai
