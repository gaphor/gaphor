"""
Activity control nodes.
"""
# vim:sw=4:et

import math
import itertools

import gobject
import pango

import diacanvas
from gaphor import UML
from gaphor import resource
from gaphor.diagram import TextElement
from elementitem import ElementItem
from nameditem import NamedItem, SimpleNamedItem, SideNamedItem
from gaphor.diagram.groupable import GroupBase


class ActivityNodeItem(ElementItem):
    """
    Basic class for simple activity nodes. Simple activity node is not
    resizable.
    """
    MARGIN = 10
    
    popup_menu = (
        'EditDelete',
    )

    def __init__(self, id=None):
        ElementItem.__init__(self, id)
        # Do not allow resizing of the node
        for h in self.handles:
            h.props.movable = False


class NamedNodeItem(ActivityNodeItem, SideNamedItem):
    """
    Abstract class which represents node item with name.
    """
    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        SideNamedItem.__init__(self)


    def on_update(self, affine):
        ActivityNodeItem.on_update(self, affine)
        SideNamedItem.on_update(self, affine)


    def on_subject_notify(self, pspec, notifiers = ()):
        ActivityNodeItem.on_subject_notify(self, pspec, notifiers)
        self._name.subject = self.subject
        self.request_update()


class InitialNodeItem(NamedNodeItem):
    """
    Representation of initial node. Initial node has name which is put near
    top-left side of node.
    """
    __uml__ = UML.InitialNode

    RADIUS = 10

    def __init__(self, id = None):
        NamedNodeItem.__init__(self, id)
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



class ActivityFinalNodeItem(NamedNodeItem):
    """
    Representation of activity final node. Activity final node has name
    which is put near right-bottom side of node.
    """

    __uml__ = UML.ActivityFinalNode

    RADIUS_1 = 10
    RADIUS_2 = 15

    def __init__(self, id = None):
        NamedNodeItem.__init__(self, id)
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

        # set name side
        self.side = self.SIDE_RIGHT + self.SIDE_BOTTOM

        self.set(width=d+2, height=d+2)

    def on_shape_iter(self):
        return iter([self._outer, self._inner])


class FlowFinalNodeItem(NamedNodeItem):
    """
    Representation of flow final node. Flow final node has name which is
    put near right-bottom side of node.
    """

    __uml__ = UML.FlowFinalNode

    RADIUS = 10

    def __init__(self, id=None):
        NamedNodeItem.__init__(self, id)
        r = self.RADIUS
        d = r * 2
        self._circle = diacanvas.shape.Ellipse()
        self._circle.ellipse((r, r), d, d)
        self._circle.set_line_width(2)

        def get_line(p1, p2):
            line = diacanvas.shape.Path()
            line.line((p1, p2))
            line.set_line_width(2)
            return line

        dr = (1 - math.sin(math.pi / 4)) * r
        self._line1 = get_line((dr, dr), (d - dr, d - dr))
        self._line2 = get_line((dr, d - dr), (d - dr, dr))

        # set name side
        self.side = self.SIDE_RIGHT + self.SIDE_BOTTOM

        self.set(width=d, height=d)


    def on_shape_iter(self):
        return iter([self._circle, self._line1, self._line2])



class FDNode(ActivityNodeItem):
    """
    Abstract class for fork and decision UI nodes. These nodes contain
    combined property, which determines if the they represent combination
    of fork/join or decision/merge nodes as described in UML
    specification.

    """
    __gproperties__ = {
        'combined': (gobject.TYPE_BOOLEAN, 'combined',
            'check if node item is combination of fork/join or decision/merge nodes',
            False,
            gobject.PARAM_READWRITE),
    }

    def __init__(self, id):
        ActivityNodeItem.__init__(self, id)
        self._combined = False
        self.set_prop_persistent('combined')


    def do_set_property(self, pspec, value):
        if pspec.name == 'combined':
            self.preserve_property('combined')
            self._combined = value
        else:
            ActivityNodeItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name == 'combined':
            return self._combined
        else:
            return ActivityNodeItem.do_get_property(self, pspec)



class DecisionNodeItem(FDNode):
    """
    Representation of decision or merge node.
    """

    __uml__ = UML.DecisionNode

    RADIUS = 15

    def __init__(self, id=None):
        FDNode.__init__(self, id)
        r = self.RADIUS
        r2 = r * 2/3
        self._diamond = diacanvas.shape.Path()
        self._diamond.line(((r2,0), (r2*2, r), (r2, r*2), (0, r)))
        self._diamond.set_cyclic(True)
        self._diamond.set_line_width(2.0)
        self.set(width=r2*2, height=r*2)

    def on_shape_iter(self):
        return iter([self._diamond])



class ForkNodeItem(FDNode, GroupBase):
    """
    Representation of fork or join node.
    """
    __uml__ = UML.ForkNode

    WIDTH  =  6.0
    HEIGHT = 45.0

    def __init__(self, id=None):
        GroupBase.__init__(self)
        FDNode.__init__(self, id)

        self._join_spec = TextElement('value', '{ joinSpec = %s }', 'and')
        self.add(self._join_spec)

        self._line = diacanvas.shape.Path()
        self._line.set_line_width(self.WIDTH)

        self.set(width = self.WIDTH, height = self.HEIGHT)
        for h in self.handles:
            h.props.movable = False
            h.props.visible = False
        self.handles[diacanvas.HANDLE_N].props.visible = True
        self.handles[diacanvas.HANDLE_S].props.visible = True
        self.handles[diacanvas.HANDLE_N].props.movable = True
        self.handles[diacanvas.HANDLE_S].props.movable = True


    def on_update(self, affine):
        """
        Update fork/join node.

        If node is join node then update also join specification.
        """
        FDNode.on_update(self, affine)
        p1 = self.handles[diacanvas.HANDLE_N].get_pos_i()
        p2 = self.handles[diacanvas.HANDLE_S].get_pos_i()
        self._line.line((p1, p2))

        w, h = self._join_spec.get_size()
        self._join_spec.update_label((self.width - w) / 2, 
            -h - self.MARGIN)

        GroupBase.on_update(self, affine)


    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Detect changes of subject.

        If subject is join node, then set subject of join specification
        text element.
        """
        FDNode.on_subject_notify(self, pspec, notifiers)
        if self.subject and isinstance(self.subject, UML.JoinNode):
            factory = resource(UML.ElementFactory)
            if not self.subject.joinSpec:
                self.subject.joinSpec = factory.create(UML.LiteralSpecification)
                self.subject.joinSpec.value = 'and'
            self._join_spec.subject = self.subject.joinSpec
        else:
            self._join_spec.subject = None
        self.request_update()


    def on_shape_iter(self):
        return iter([self._line])
