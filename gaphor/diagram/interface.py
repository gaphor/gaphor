'''
InterfaceItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import math
import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.implementation import ImplementationItem
from nameditem import NamedItem
from klass import ClassItem
from relationship import RelationshipItem


def make_arc(radius, edges, q=0):
    """Create a tupple of edges points, which represent a 90 degrees
    arc in the first quadrant
    """
    points = []
    sin = math.sin
    cos = math.cos
    pi2 = math.pi/2
    for i in xrange(edges + 1):
        n = (pi2 * i) / edges + pi2*q
        points.append((cos(n) * radius, sin(n) * radius))
    return points

def alter_arc(arc, offsetx=0, offsety=0):
    return [(x+offsetx, y+offsety) for x, y in arc]

class InterfaceItem(ClassItem):
    """This item represents an interface drawn as a dot. The class-like
    representation is provided by ClassItem. These representations can be
    switched by using the Fold and Unfold actions.

    TODO (see also DependencyItem): when a Usage dependency is connected to
          the interface, draw a line, but not all the way to the connecting
          handle. Stop drawing the line 'x' points earlier. 
    """
    RADIUS=10

    PROVIDED = 1
    REQUIRED = 2
    WIRING = 3

    # This are the half-circles used to draw the 'requires' interface.
    _required_arcs = [
        # Top
        alter_arc(make_arc(14, edges=10, q=2) + make_arc(14,edges=10, q=3), offsetx=10, offsety=12),
        # Right
        alter_arc(make_arc(14, edges=10, q=3) + make_arc(14,edges=10, q=0), offsetx=8, offsety=10),
        # Bottom
        alter_arc(make_arc(14, edges=10, q=0) + make_arc(14,edges=10, q=1), offsetx=10, offsety=8),
        # Left
        alter_arc(make_arc(14, edges=10, q=1) + make_arc(14,edges=10, q=2), offsetx=12, offsety=10)
    ]

    #popup_menu = NamedItem.popup_menu + ('Unfold',)

    def __init__(self, id=None):
        ClassItem.__init__(self, id)

        #self.drawing_style = self.DRAW_ICON

        self.usage_items = 0
        self.implementation_items = 0

        self._interface = diacanvas.shape.Ellipse()
        self._interface.set_line_width(2.0)
        self._interface.set_fill(1)
        self._interface.set_fill_color(diacanvas.color(255, 255, 255))

        self._required = diacanvas.shape.Path()
        self._required.set_line_width(2.0)

    def set_drawing_style(self, style):
        """In addition to setting the drawing style, the handles are
        make non-movable if the icon (folded) style is used.
        """
        ClassItem.set_drawing_style(self, style)
        if self.drawing_style == self.DRAW_ICON:
            r2 = self.RADIUS * 2
            self.set(height=r2, width=r2)
            # Do not allow resizing of the node
            for h in self.handles:
                h.set_property('movable', 0)
        else:
            # Do allow resizing of the node
            for h in self.handles:
                h.set_property('movable', 1)

    def get_popup_menu(self):
        if self.drawing_style == self.DRAW_ICON:
            return NamedItem.popup_menu + ('Unfold',)
        else:
            return ClassItem.get_popup_menu(self)

    def is_folded(self):
        return self.drawing_style == self.DRAW_ICON

    def update_stereotype(self):
        if not ClassItem.update_stereotype(self):
            self.set_stereotype('interface')
 
    def update_icon(self, affine):
        right, top = self.handles[diacanvas.HANDLE_NE].get_pos_i()
        left, bottom = self.handles[diacanvas.HANDLE_SW].get_pos_i()
        right -= 0.1
        left += 0.1
        top += 0.1
        bottom -= 0.1

        # Figure out if this interface represents a required, provided
        # or wired look.
        arc_index = 1
        self.usage_items = 0
        self.implementation_items = 0
        for connected_item in self.canvas.select(lambda i: i.handles and \
                (i.handles[0].connected_to is self or \
                i.handles[-1].connected_to is self)):
            if isinstance(connected_item, DependencyItem) and \
                    connected_item.dependency_type is UML.Usage:
                self.usage_items += 1
                # Find out on which side the usage is connected
                x, y = connected_item.handles[0].get_pos_w()
                x, y = self.affine_point_w2i(x, y)
                if x >= right:
                    arc_index = 1
                elif x <= left:
                    arc_index = 3
                elif y <= top:
                    arc_index = 0
                elif y >= bottom:
                    arc_index = 2
            if isinstance(connected_item, ImplementationItem):
                self.implementation_items += 1

        # Center the text
        r = self.RADIUS
        r2 = r * 2
        w, h = self.get_name_size()
        #self.set(min_width=w, min_height=h)

        self.update_name(x=r - w/2, y=r2, width=w, height=h)

        #NamedItem.on_update(self, affine)

        look_type = self.look_type
        if look_type & self.REQUIRED:
            line = self._required_arcs[arc_index]
            self._required.line(line)
            self.expand_bounds(4)
        if look_type & self.PROVIDED:
            self._interface.ellipse((r, r), r2, r2)

        # update the bounding box:
        #ulx, uly, lrx, lry = self.bounds
        #if w > r2:
        #    ulx = r - w/2
        #    lrx = r + w/2
        #self.set_bounds((ulx, uly-1, lrx+1, lry+h))

    def on_update(self, affine):
        ClassItem.on_update(self, affine)

        # update bounding box
        if self.drawing_style == self.DRAW_ICON:
            r = self.RADIUS
            r2 = r * 2
            w, h = self.get_name_size()
            ulx, uly, lrx, lry = self.bounds
            if w > r2:
                ulx = r - w/2
                lrx = r + w/2
            self.set_bounds((ulx, uly-1, lrx+1, lry+h))

    def on_shape_iter(self):
        if self.drawing_style == self.DRAW_ICON:
            look_type = self.look_type
            if look_type & self.REQUIRED:
                yield self._required
            if look_type & self.PROVIDED:
                yield self._interface

        for s in ClassItem.on_shape_iter(self):
            yield s

    def on_connect_handle(self, handle):
        self.request_update()
        return ClassItem.on_connect_handle(self, handle)

    def on_disconnect_handle(self, handle):
        self.request_update()
        return ClassItem.on_disconnect_handle(self, handle)

    def get_look_type(self):
        if self.usage_items > 0 and self.implementation_items == 0:
            return self.REQUIRED
        elif self.usage_items > 0 and self.implementation_items > 0:
            return self.WIRING
        else:
            return self.PROVIDED

    look_type = property(get_look_type)


initialize_item(InterfaceItem, UML.Interface)
