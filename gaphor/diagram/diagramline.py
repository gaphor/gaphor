# vim:sw=4:et
"""Basic functionality for line-like objects on a diagram.
"""

import gobject
import diacanvas

class DiagramLine(diacanvas.CanvasLine):
    """Gaphor wrapper for lines."""

    def __init__(self):
        #diacanvas.CanvasLine.__init__(self)
        self.__gobject_init__()

    def save (self, save_func):
        for prop in ('affine', 'line_width', 'color', \
                     'cap', 'join', 'orthogonal', 'horizontal'):
            save_func(prop, self.get_property(prop))
        points = [ ]
        for h in self.handles:
            pos = h.get_pos_i ()
            points.append (pos)
        save_func('points', points)
        c = self.handles[0].connected_to
        if c:
            save_func('head_connection', c, reference=True)
        c = self.handles[-1].connected_to
        if c:
            save_func ('tail_connection', c, reference=True)

    def load (self, name, value):
        if name == 'points':
            points = eval(value)
            self.set_property('head_pos', points[0])
            self.set_property('tail_pos', points[1])
            for p in points[2:]:
                item.set_property ('add_point', p)
        elif name == 'head_connection':
            self._load_head_connection = value
        elif name == 'tail_connection':
            self._load_tail_connection = value
        else:
            self.set_property(name, eval(value))

    def postload(self):
        if hasattr(self, '_load_head_connection'):
            self._load_head_connection.connect_handle (self.handles[0])
            del self._load_head_connection
        if hasattr(self, '_load_tail_connection'):
            self._load_tail_connection.connect_handle (self.handles[-1])
            del self._load_tail_connection

    def has_capability(self, capability):
        #log.debug('Relationship: checking capability %s' % capability)
        if capability == 'orthogonal':
            return self.get_property('orthogonal')
        elif capability == 'del_segment':
            if self.get_property('orthogonal'):
                return len(self.handles) > 3
            else:
                return len(self.handles) > 2
        return False

    # Gaphor Connection Protocol
    #
    # The item a handle is connecting to is in charge of the connection
    # cyclus. However it informs the item it is connecting to by means of
    # the four methods defined below. The items that are trying to connect
    # (mostly Relationship objects or CommentLines) know what kind of item
    # they are allowed to connect to.

    def find_relationship(self, head_subject, tail_subject):
        """Find an already existing relationship between head_subject and
        tail_subject. The following things should be taken into account:
        - The returned relationship object will be used for this item.
        - The relationship should not already exist in the canvas.
        """
        return None

    def allow_connect_handle(self, handle, connecting_to):
        """This method is called by a canvas item if the user tries to
        connect this object's handle. allow_connect_handle() checks if
        the line is allowed to be connected. In this case that means
        that one end of the line should be connected to a Relationship.
        Returns: True if connection is allowed, False otherwise.
        """
        return False

    def confirm_connect_handle (self, handle):
        """This method is called after a connection is established.
        This method sets the internal state of the line and updates
        the data model. Returns nothing
        """
        pass

    def allow_disconnect_handle (self, handle):
        """ If a handle wants to disconnect, this method is called first.
        This method is here mainly for the sake of completeness, since it
        is quite unlikely that a handle is not allowed to disconnect.
        """
        return 1

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """This method is called to do some cleanup after 'self' has been
        disconnected from 'was_connected_to'.
        """
        pass


gobject.type_register(DiagramLine)
diacanvas.set_callbacks(DiagramLine)

