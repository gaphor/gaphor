"""
Basic functionality for canvas line based items on a diagram.
"""

import itertools

import diacanvas
from diagramitem import DiagramItem
from gaphor.diagram import LineItemMeta

class LineItem(diacanvas.CanvasLine, DiagramItem):
    """
    Base class for diagram lines.
    """

    __metaclass__ = LineItemMeta

    __gproperties__ = DiagramItem.__gproperties__
    __gsignals__ = DiagramItem.__gsignals__

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def __init__(self, id = None):
        #diacanvas.CanvasLine.__init__(self)
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        #super(LineItem, self).__init__(id)
        self.props.horizontal = False


    # Gaphor Connection Protocol
    #
    # The item a handle is connecting to is in charge of the connection
    # cyclus. However it informs the item it is connecting to by means of
    # the four methods defined below. The items that are trying to connect
    # (mostly Relationship objects or CommentLines) know what kind of item
    # they are allowed to connect to.
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
        return True

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """This method is called to do some cleanup after 'self' has been
        disconnected from 'was_connected_to'.
        """
        pass


    # DiaCanvasItem callbacks
    def on_glue(self, handle, wx, wy):
        return self._on_glue(handle, wx, wy, diacanvas.CanvasLine)

    def on_connect_handle (self, handle):
        return self._on_connect_handle(handle, diacanvas.CanvasLine)

    def on_disconnect_handle (self, handle):
        return self._on_disconnect_handle(handle, diacanvas.CanvasLine)


    def on_update (self, affine):
        diacanvas.CanvasLine.on_update(self, affine)

        # update stereotype
        # fixme: use util function
        sw, sh = self._stereotype.to_pango_layout(True).get_pixel_size()

        handles = self.handles
        middle = len(handles)/2
        p1 = handles[middle-1].get_pos_i()
        p2 = handles[middle].get_pos_i()

        x = p1[0] > p2[0] and sw + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] <= p2[1] and sh or 0
        y = (p1[1] + p2[1]) / 2.0 - y

        self._stereotype.set_pos((x, y))
        self._stereotype.set_max_width(sw)
        self._stereotype.set_max_height(sh)

        b1 = x, y, sw, sh

        b2 = self.bounds
        self.set_bounds((min(b1[0], b2[0]), min(b1[1], b2[1]),
                         max(b1[2] + b1[0], b2[2]), max(b1[3] + b1[1], b2[3])))

        self.update_stereotype()


    def on_shape_iter(self):
        return itertools.chain(diacanvas.CanvasLine.on_shape_iter(self), self._shapes)



class DiagramLine(LineItem):
    """
    Gaphor lines. This line is serializable and has a popup
    menu.
    """

    popup_menu = LineItem.popup_menu + (
        'separator', 
        'AddSegment',
        'DeleteSegment',
        'Orthogonal',
        'OrthogonalAlignment',
        'separator',
        'EditDelete'
    )

    def do_set_property (self, pspec, value):
        pass

    def do_get_property(self, pspec):
        pass

    def save (self, save_func):
        LineItem.save(self, save_func)
        for prop in ('affine', 'color', 'orthogonal', 'horizontal'):
            save_func(prop, self.get_property(prop))
        points = [ ]
        for h in self.handles:
            pos = h.get_pos_i ()
            points.append (pos)
        save_func('points', points)
        c = self.handles[0].connected_to
        if c:
            save_func('head-connection', c, reference=True)
        c = self.handles[-1].connected_to
        if c:
            save_func('tail-connection', c, reference=True)

    def load (self, name, value):
        if name == 'points':
            points = eval(value)
            self.set_property('head_pos', points[0])
            self.set_property('tail_pos', points[1])
            for p in points[2:]:
                self.set_property ('add_point', p)
        elif name in ('head_connection', 'head-connection'):
            self._load_head_connection = value
        elif name in ('tail_connection', 'tail-connection'):
            self._load_tail_connection = value
        else:
            LineItem.load(self, name, value)

    def postload(self):
        if hasattr(self, '_load_head_connection'):
            self._load_head_connection.connect_handle(self.handles[0])
            del self._load_head_connection
        if hasattr(self, '_load_tail_connection'):
            self._load_tail_connection.connect_handle(self.handles[-1])
            del self._load_tail_connection
        LineItem.postload(self)



class FreeLine(LineItem):
    """
    A line with disabled last handle. This allows to create diagram items,
    which have one or more additional lines.

    Last handle is usually attached to a point of diagram item. This point
    is called main point.
    """
    def __init__(self, id = None, mpt = None):
        LineItem.__init__(self, id)

        # expose first handle
        self._handle = self.handles[0]

        # disable last handle, it should be in main point
        h = self.handles[-1]
        h.props.movable = False
        h.props.connectable = False
        h.props.visible = False

        self._main_point = mpt

        if self._main_point is None:
            self._main_point = 0, 0


    def on_update(self, affine):
        self.handles[-1].set_pos_i(*self._main_point)
        self._handle.set_pos_i(*self._handle.get_pos_i()) # really strange, but we have to do this

        LineItem.on_update(self, affine)

# vim:sw=4:et
