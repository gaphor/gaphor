'''
InterfaceItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
import gaphor.diagram.association
import gaphor.diagram.implementation
from nameditem import NamedItem
from relationship import RelationshipItem


class InterfaceItem(NamedItem):
    """This item represents an interface drawn as a dot. The class-like
    representation is provided by ClassItem. These representations can be switched
    by using the Fold and Unfold actions.

    TODO: Provided interfaces are shown by a Implementation dependency,
          Required interfaces are shown by a Usage dependency (not association).
          
          Interfaces may also be used to specify required interfaces, which are
          specified by a usage dependency between the classifier and the
          corresponding interfaces. Required interfaces specify services that a
          classifier needs in order to perform its function and fulfill its own
          obligations to its clients.
    """
    RADIUS=10

    PROVIDED = 0
    REQUIRED = 1
    WIRING = 2

    popup_menu = NamedItem.popup_menu + ('Unfold',)

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        r2 = self.RADIUS * 2
        self.set(height=r2, width=r2)

        self.association_items = 0
        self.implementation_items = 0

        self._interface = diacanvas.shape.Ellipse()
        self._interface.set_line_width(2.0)
        self._interface.set_fill(1)
        self._interface.set_fill_color(diacanvas.color(255, 255, 255))

        self._required = diacanvas.shape.Ellipse()
        self._required.set_line_width(2.0)
        self._required.set_fill(1)
        self._required.set_fill_color(diacanvas.color(0, 0, 255))

        self._wiring = diacanvas.shape.Ellipse()
        self._wiring.set_line_width(2.0)
        self._wiring.set_fill(1)
        self._wiring.set_fill_color(diacanvas.color(0, 0, 0))

        # Do not allow resizing of the node
        for h in self.handles:
            h.set_property('movable', 0)

    def on_update(self, affine):

        # Figure out if this interface represents a required, provided or wired look.
        self.association_items = 0
        self.implementation_items = 0
        for connected_item in self.canvas.select(lambda i: i.handles and \
                (i.handles[0].connected_to is self or \
                i.handles[-1].connected_to is self)):
            if isinstance(connected_item,
                    gaphor.diagram.association.AssociationItem):
                self.association_items += 1
            if isinstance(connected_item,
                    gaphor.diagram.implementation.ImplementationItem):
                self.implementation_items += 1

        # Center the text
        r = self.RADIUS
        r2 = r * 2
        w, h = self.get_name_size()
        #self.set(min_width=w, min_height=h)

        look_type = self.look_type
        if look_type == self.REQUIRED:
            self._required.ellipse((r, r), r2, r2)
        elif look_type == self.WIRING:
            self._wiring.ellipse((r, r), r2, r2)
        elif look_type == self.PROVIDED:
            self._interface.ellipse((r, r), r2, r2)

        self.update_name(x=r - w/2, y=r2, width=w, height=h)

        NamedItem.on_update(self, affine)

        # update the bounding box:
        ulx, uly, lrx, lry = self.bounds
        if w > r2:
            ulx = r - w/2
            lrx = r + w/2
        self.set_bounds((ulx, uly-1, lrx+1, lry+h))

    def on_handle_motion(self, handle, wx, wy, mask):
        # Make sure the element works with diacanavs2 <= 0.12.0.
        if handle not in self.handles[:7]:
            return wx, wy
        return NamedItem.on_handle_motion(self, handle, wx, wy, mask)

    def on_shape_iter(self):
        look_type = self.look_type
        if look_type == self.REQUIRED:
            look = self._required
        elif look_type == self.WIRING:
            look = self._wiring
        elif look_type == self.PROVIDED:
            look = self._interface

        yield look

        for s in NamedItem.on_shape_iter(self):
            yield s

    def on_connect_handle(self, handle):
        self.request_update()
        return NamedItem.on_connect_handle(self, handle)

    def on_disconnect_handle(self, handle):
        self.request_update()
        return NamedItem.on_disconnect_handle(self, handle)

    def _getLookType(self):
        if self.association_items > 0 and self.implementation_items == 0:
            return self.REQUIRED
        elif self.association_items > 0 and self.implementation_items > 0:
            return self.WIRING
        else:
            return self.PROVIDED

    look_type = property(_getLookType)


initialize_item(InterfaceItem, UML.Interface)
