# vim:sw=4:et
'''
CommentLine -- A line that connects a comment to another model element.

TODO: Why do we lose the __id property when we do a get_property after a model
has been loaded. It works okay when creating new items.
'''

import gobject
import diacanvas
import gaphor.UML as UML

from diagramline import DiagramLine

class CommentLineItem(DiagramLine):

    def __init__(self, id=None):
        #diacanvas.CanvasLine.__init__(self)
        DiagramLine.__init__(self)
        self._id = id
        self.set_property('dash', (7.0, 5.0))

    id = property(lambda self: self._id, doc='Id')

    def on_glue(self, handle, wx, wy):
        "No connections are allowed on a CommentLine."
        return None

    def on_connect_handle(self, handle):
        "No connections are allows to the CommentLine."
        return 0

    def on_disconnect_handle(self, handle):
        "No connections are allows to the CommentLine."
        return 0

    # Gaphor Connection Protocol

    def allow_connect_handle(self, handle, connecting_to):
        """See DiagramLine.allow_connect_handle().
        """
        h = self.handles
        c1 = h[0].connected_to
        c2 = h[-1].connected_to
        # OK if both sides are not connected yet.
        if not c1 and not c2:
            return 1
        
        if handle is h[0]:
            c1 = connecting_to
        elif handle is h[-1]:
            c2 = connecting_to
        else:
            raise AttributeError, 'handle should be the first or the last handle of the CommentLine'

        # We should not connect if both ends will become a Comment
        if isinstance(c1.subject, UML.Comment) and \
                isinstance(c2.subject, UML.Comment):
            return 0
        # Also do not connect if both ends are non-Comments
        if not isinstance(c1.subject, UML.Comment) and \
                not isinstance(c2.subject, UML.Comment):
            return 0

        # Allow connection
        return 1

    def confirm_connect_handle (self, handle):
        """See DiagramLine.confirm_connect_handle().
        """
        #print 'confirm_connect_handle', handle
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            if isinstance (s1, UML.Comment):
                s1.annotatedElement = s2
            elif isinstance (s2, UML.Comment):
                s2.annotatedElement = s1
            else:
                raise TypeError, 'One end of the CommentLine should connect to a Comment'

    def allow_disconnect_handle (self, handle):
        """See DiagramLine.allow_disconnect_handle().
        """
        return 1

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        c1 = None
        c2 = None
        if handle is self.handles[0]:
            c1 = was_connected_to
            c2 = self.handles[-1].connected_to
        elif handle is self.handles[-1]:
            c1 = self.handles[0].connected_to
            c2 = was_connected_to
        
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            if isinstance (s1, UML.Comment):
                del s1.annotatedElement[s2]
            elif isinstance (s2, UML.Comment):
                del s2.annotatedElement[s1]
            else:
                raise TypeError, 'One end of the CommentLine should connect to a Comment. How could this connect anyway?'

gobject.type_register(CommentLineItem)
diacanvas.set_callbacks(CommentLineItem)

