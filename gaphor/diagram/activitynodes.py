"""InitialNode and ActivityFinalNode.
"""
# vim:sw=4:et

import math

import gobject
import pango
import diacanvas
from gaphor import UML
from gaphor.diagram import initialize_item
from elementitem import ElementItem
from nameditem import NamedItem

class ActivityNodeItem(ElementItem):
    
    popup_menu = (
        'EditDelete',
    )

    def __init__(self, id=None):
        ElementItem.__init__(self, id)
        # Do not allow resizing of the node
        for h in self.handles:
            h.set_property('movable', False)


class InitialNodeItem(NamedItem):
    RADIUS = 10
    MARGIN_Y = RADIUS*2

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        for h in self.handles:
            h.set_property('movable', False)
        r = self.RADIUS
        d = r * 2
        self._circle = diacanvas.shape.Ellipse()
        self._circle.ellipse((r, r), d, d)
        self._circle.set_line_width(0.01)
        self._circle.set_fill(diacanvas.shape.FILL_SOLID)
        self._circle.set_fill_color(diacanvas.color(0, 0, 0, 255))
        self.set(width=d, height=d)
       
    def on_update(self, affine):
        # Center the text
        w, h = self.get_name_size()
        self.set(min_width=w,
                 min_height=h + self.MARGIN_Y)
        self.update_name(x=0, y=(self.height - h),
                         width=self.width, height=h)

        NamedItem.on_update(self, affine)
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        for s in NamedItem.on_shape_iter(self):
            yield s
        for c in iter([self._circle]):
            yield c


class ActivityFinalNodeItem(ActivityNodeItem):
    RADIUS_1 = 10
    RADIUS_2 = 15

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        r = self.RADIUS_2
        d = self.RADIUS_1 * 2
        self._inner = diacanvas.shape.Ellipse()
        self._inner.ellipse((r + 1, r + 1), d, d)
        self._inner.set_line_width(0.01)
        self._inner.set_fill(diacanvas.shape.FILL_SOLID)
        self._inner.set_fill_color(diacanvas.color(0, 0, 0, 255))

        d = r * 2
        self._outer = diacanvas.shape.Ellipse()
        self._outer.ellipse((r + 1, r + 1), d, d)
        self._outer.set_line_width(2)
        self._outer.set_color(diacanvas.color(0, 0, 0, 255))

        self.set(width=d+2, height=d+2)

    def on_shape_iter(self):
        return iter([self._outer, self._inner])


class FlowFinalNodeItem(ActivityNodeItem):
    RADIUS = 10

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        r = self.RADIUS
        d = r * 2
        self._circle = diacanvas.shape.Ellipse()
        self._circle.ellipse((r, r), d, d)
        self._circle.set_line_width(2)

        def getLine(p1, p2):
            line = diacanvas.shape.Path()
            line.line((p1, p2))
            line.set_line_width(2)
            return line

        dr = (1 - math.sin(math.pi / 4)) * r
        self._line1 = getLine((dr, dr), (d - dr, d - dr))
        self._line2 = getLine((dr, d - dr), (d - dr, dr))

        self.set(width=d, height=d)

    def on_shape_iter(self):
        return iter([self._circle, self._line1, self._line2])


class DecisionNodeItem(ActivityNodeItem):
    RADIUS = 15

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        r = self.RADIUS
        r2 = r * 2/3
        self._diamond = diacanvas.shape.Path()
        self._diamond.line(((r2,0), (r2*2, r), (r2, r*2), (0, r)))
        self._diamond.set_cyclic(True)
        self._diamond.set_line_width(2.0)
        self.set(width=r2*2, height=r*2)

    def on_shape_iter(self):
        return iter([self._diamond])



class ForkNodeItem(ActivityNodeItem):
    WIDTH = 6.0

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        self._line = diacanvas.shape.Path()
        self._line.set_line_width(self.WIDTH)

        self.handles[0].set_property('movable', True)
        self.handles[3].set_property('movable', True)

    def on_update(self, affine):
        ActivityNodeItem.on_update(self, affine)
        self._line.line(((0, 0), (0, self.height)))
        self.set(width=self.WIDTH, height=self.height)

    def on_shape_iter(self):
        return iter([self._line])



initialize_item(ActivityNodeItem)
initialize_item(InitialNodeItem, UML.InitialNode)
initialize_item(ActivityFinalNodeItem, UML.ActivityFinalNode)
initialize_item(FlowFinalNodeItem, UML.FlowFinalNode)
initialize_item(DecisionNodeItem, UML.DecisionNode)
initialize_item(ForkNodeItem, UML.ForkNode)
