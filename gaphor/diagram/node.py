"""InitialNode and ActivityFinalNode.
"""
# vim:sw=4:et

import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from elementitem import ElementItem

class NodeItem(ElementItem):
    
    popup_menu = (
        'EditDelete',
    )

    def __init__(self, id=None):
        ElementItem.__init__(self, id)
        # Do not allow resizing of the node
        for h in self.handles:
            h.set_property('movable', 0)


class InitialNodeItem(NodeItem):
    RADIUS = 10

    def __init__(self, id=None):
        NodeItem.__init__(self, id)
        r = self.RADIUS
        d = r * 2
        self._circle = diacanvas.shape.Ellipse()
        self._circle.ellipse((r, r), d, d)
        self._circle.set_line_width(0.01)
        self._circle.set_fill(diacanvas.shape.FILL_SOLID)
        self._circle.set_fill_color(diacanvas.color(0, 0, 0, 255))
        self.set(width=d, height=d)

    def on_shape_iter(self):
        return iter([self._circle])


class ActivityFinalNodeItem(NodeItem):
    RADIUS_1 = 10
    RADIUS_2 = 15

    def __init__(self, id=None):
        NodeItem.__init__(self, id)
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


class DecisionNodeItem(NodeItem):
    RADIUS = 15

    def __init__(self, id=None):
        NodeItem.__init__(self, id)
        r = self.RADIUS
        r2 = r * 2/3
        self._diamond = diacanvas.shape.Path()
        self._diamond.line(((r2,0), (r2*2, r), (r2, r*2), (0, r)))
        self._diamond.set_cyclic(True)
        self._diamond.set_line_width(2.0)
        self.set(width=r2*2, height=r*2)

    def on_shape_iter(self):
        return iter([self._diamond])


initialize_item(NodeItem)
initialize_item(InitialNodeItem, UML.InitialNode)
initialize_item(ActivityFinalNodeItem, UML.ActivityFinalNode)
initialize_item(DecisionNodeItem, UML.DecisionNode)
