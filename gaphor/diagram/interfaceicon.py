"""
This module contains several interface icon shape implementation::
    - provided interface
    - required interface
    - assembled provided and required interfaces
    - interface as a line used when connected to assembly connector
"""

import itertools
import math

import diacanvas
from gaphor.diagram import rotatable

class InterfaceIconBase(object):
    """
    Basic class for interface icons like::
        - provided interface
        - required interface
    """
    def __init__(self, parent):
        self.parent = parent
        self.show_bar = True

        self._bar = diacanvas.shape.Path()
        self._bar.set_line_width(2.0)

        self._circle = self.get_circle()
        self._circle.set_line_width(2.0)

        self.width = self.height = (self.RADIUS + self.BAR_WIDTH) * 2


    handles = property(lambda self: self.parent.handles)


    def update_icon(self):
        dir = self.dir

        dh = self.handles[rotatable.dir2dh[dir]]
        p1 = dh.get_pos_i()

        bw = self.BAR_WIDTH
        p2 = p1[0] + bw * rotatable.xdirsign[dir], \
            p1[1] + bw * rotatable.ydirsign[dir]

        self._bar.line((p1, p2))

        self.draw_circle()


    def get_provided_pos_w(self):
        dir = rotatable.dirside[self.dir]
        return self.handles[rotatable.dir2dh[self.dir]].get_pos_w()


    def get_required_pos_w(self):
        return self.handles[rotatable.dir2dh[self.dir]].get_pos_w()


    def get_provided_pos_i(self):
        dir = rotatable.dirside[self.dir]
        return self.handles[rotatable.dir2dh[self.dir]].get_pos_i()


    def get_required_pos_i(self):
        return self.handles[rotatable.dir2dh[self.dir]].get_pos_i()


    def on_shape_iter(self):
        if self.show_bar:
            yield self._bar
        yield self._circle



class ProvidedInterfaceIcon(InterfaceIconBase):
    """
    Provided interface icon.
    """

    RADIUS = 10
    BAR_WIDTH = 8

    dir = property(lambda self: self.parent.props.dir)

    def get_circle(self):
        return diacanvas.shape.Ellipse()


    def draw_circle(self):
        r = self.RADIUS + self.BAR_WIDTH
        d = 2 * self.RADIUS
        self._circle.ellipse((r, r), d, d)



class RequiredInterfaceIcon(InterfaceIconBase):
    """
    Required interface icon.
    """

    RADIUS = 14
    BAR_WIDTH = 4

    dir = property(lambda self: rotatable.dirside[self.parent.props.dir])

    def get_circle(self): # todo: change to arc
        return diacanvas.shape.Path()


    def draw_circle(self):
        self._circle.line(required_arcs[self.dir])



class AssembledInterfaceIcon(object):
    """
    Assembled provided and required interface icons.
    """
    def __init__(self, parent):
        self.parent = parent
        self._provided = ProvidedInterfaceIcon(parent)
        self._required = RequiredInterfaceIcon(parent)

        self.width = self._provided.width
        self.height = self._provided.height


    def update_icon(self):
        self._provided.update_icon()
        self._required.update_icon()


    def on_shape_iter(self):
        return itertools.chain(self._provided.on_shape_iter(),
            self._required.on_shape_iter())


    def get_provided_pos_w(self):
        return self._provided.get_provided_pos_w()


    def get_required_pos_w(self):
        return self._required.get_required_pos_w()


    def get_provided_pos_i(self):
        return self._provided.get_provided_pos_i()


    def get_required_pos_i(self):
        return self._required.get_required_pos_i()



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

required_arcs = (
    # Top
    alter_arc(make_arc(14, edges=10, q=2) + make_arc(14, edges=10, q=3), offsetx=18, offsety=18),
    # Right
    alter_arc(make_arc(14, edges=10, q=3) + make_arc(14, edges=10, q=0), offsetx=18, offsety=18),
    # Bottom
    alter_arc(make_arc(14, edges=10, q=0) + make_arc(14, edges=10, q=1), offsetx=18, offsety=18),
    # Left
    alter_arc(make_arc(14, edges=10, q=1) + make_arc(14, edges=10, q=2), offsetx=18, offsety=18),
)
