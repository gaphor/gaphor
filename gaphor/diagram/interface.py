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
from nameditem import NamedItem
from relationship import RelationshipItem


class InterfaceItem(NamedItem):
    RADIUS=10

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        r2 = self.RADIUS * 2
        self.set(height=r2, width=r2)
        self._interface = diacanvas.shape.Ellipse()
        self._interface.set_line_width(2.0)
        self._interface.set_fill(1)
        self._interface.set_fill_color(diacanvas.color(255, 255, 255))

        # Do not allow resizing of the node
        for h in self.handles:
            h.set_property('movable', 0)

    def on_update(self, affine):
        # Center the text
        r = self.RADIUS
        r2 = r * 2
        w, h = self.get_name_size()
        #self.set(min_width=w, min_height=h)
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
        """Make sure the element works with diacanavs2 <= 0.12.0.
        """
        if handle not in self.handles[:7]:
            return wx, wy
        return NamedItem.on_handle_motion(self, handle, wx, wy, mask)

    def on_shape_iter(self):
        yield self._interface
        for s in NamedItem.on_shape_iter(self):
            yield s

#    def on_editable_start_editing(self, shape):
#        NamedItem.on_editable_start_editing(self, shape)
#        self._name.set_max_width(0)

initialize_item(InterfaceItem, UML.Interface)
