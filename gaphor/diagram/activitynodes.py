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
from gaphor.diagram.groupable import GroupBase
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.align import H_ALIGN_LEFT, H_ALIGN_RIGHT, V_ALIGN_BOTTOM


class ActivityNodeItem(NamedItem):
    """
    Basic class for simple activity nodes. Simple activity node is not
    resizable.
    """
    __o_align__ = True

    def __init__(self, id = None):
        NamedItem.__init__(self, id)
        # Do not allow resizing of the node
        for h in self.handles:
            h.props.movable = False


class InitialNodeItem(ActivityNodeItem):
    """
    Representation of initial node. Initial node has name which is put near
    top-left side of node.
    """
    __uml__     = UML.InitialNode
    __s_align__ = H_ALIGN_LEFT
    
    RADIUS = 10

    def create_border(self):
        r = self.RADIUS
        d = r * 2
        circle = diacanvas.shape.Ellipse()
        circle.ellipse((r, r), d, d)
        circle.set_line_width(0.01)
        circle.set_fill(diacanvas.shape.FILL_SOLID)
        circle.set_fill_color(diacanvas.color(0, 0, 0, 255))
        self.set(width = d, height = d)
        return circle


    def draw_border(self):
        """
        Draw nothing as initial node does not change.
        """
        pass


class ActivityFinalNodeItem(ActivityNodeItem):
    """
    Representation of activity final node. Activity final node has name
    which is put near right-bottom side of node.
    """

    __uml__      = UML.ActivityFinalNode
    __s_align__  = H_ALIGN_RIGHT
    __s_valign__ = V_ALIGN_BOTTOM

    RADIUS_1 = 10
    RADIUS_2 = 15

    def create_border(self):
        r = self.RADIUS_2
        d = self.RADIUS_1 * 2
        self._inner = diacanvas.shape.Ellipse()
        self._inner.ellipse((r + 1, r + 1), d, d)
        self._inner.set_line_width(0.01)
        self._inner.set_fill(diacanvas.shape.FILL_SOLID)
        self._inner.set_fill_color(diacanvas.color(0, 0, 0, 255))

        d = r * 2
        border = diacanvas.shape.Ellipse()
        border.ellipse((r + 1, r + 1), d, d)
        border.set_line_width(2)
        border.set_color(diacanvas.color(0, 0, 0, 255))

        self.set(width = d + 2, height = d + 2)
        return border


    def draw_border(self):
        """
        Draw nothing as activity final node does not change.
        """
        pass


    def on_shape_iter(self):
        return itertools.chain([self._inner], ActivityNodeItem.on_shape_iter(self))


class FlowFinalNodeItem(ActivityNodeItem):
    """
    Representation of flow final node. Flow final node has name which is
    put near right-bottom side of node.
    """

    __uml__      = UML.FlowFinalNode
    __s_align__  = H_ALIGN_RIGHT
    __s_valign__ = V_ALIGN_BOTTOM

    RADIUS = 10

    def create_border(self):
        r = self.RADIUS
        d = r * 2
        border = diacanvas.shape.Ellipse()
        border.ellipse((r, r), d, d)
        border.set_line_width(2)

        def get_line(p1, p2):
            line = diacanvas.shape.Path()
            line.line((p1, p2))
            line.set_line_width(2)
            return line

        dr = (1 - math.sin(math.pi / 4)) * r
        self._line1 = get_line((dr, dr), (d - dr, d - dr))
        self._line2 = get_line((dr, d - dr), (d - dr, dr))

        self.set(width = d, height = d)

        return border


    def draw_border(self):
        """
        Draw nothing as flow final node does not change.
        """
        pass


    def on_shape_iter(self):
        return itertools.chain(ActivityNodeItem.on_shape_iter(self), [self._line1, self._line2])



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

    __uml__   = UML.DecisionNode
    __s_align__ = H_ALIGN_LEFT

    RADIUS = 15

    def create_border(self):
        r = self.RADIUS
        r2 = r * 2/3

        diamond = diacanvas.shape.Path()
        diamond.line(((r2,0), (r2*2, r), (r2, r*2), (0, r)))
        diamond.set_cyclic(True)
        diamond.set_line_width(2.0)

        self.set(width = r2 * 2, height = r * 2)

        return diamond


    def draw_border(self):
        """
        Draw nothing as decision node does not change.
        """
        pass



class ForkNodeItem(FDNode, GroupBase):
    """
    Representation of fork or join node.
    """
    __uml__      = UML.ForkNode
    __s_valign__ = V_ALIGN_BOTTOM

    WIDTH  =  6.0
    HEIGHT = 45.0
    MARGIN = 10

    def __init__(self, id=None):
        GroupBase.__init__(self)
        FDNode.__init__(self, id)

        self._join_spec = TextElement('value', '{ joinSpec = %s }', 'and')
        self.add(self._join_spec)

        for h in self.handles:
            h.props.movable = False
            h.props.visible = False
        self.handles[diacanvas.HANDLE_N].props.visible = True
        self.handles[diacanvas.HANDLE_S].props.visible = True
        self.handles[diacanvas.HANDLE_N].props.movable = True
        self.handles[diacanvas.HANDLE_S].props.movable = True


    def create_border(self):
        line = diacanvas.shape.Path()
        line.set_line_width(self.WIDTH)

        self.set(width = self.WIDTH, height = self.HEIGHT)
        return line


    def draw_border(self):
        """
        Draw line between central handles.
        """
        p1 = self.handles[diacanvas.HANDLE_N].get_pos_i()
        p2 = self.handles[diacanvas.HANDLE_S].get_pos_i()
        self._border.line((p1, p2))


    def on_update(self, affine):
        """
        Update fork/join node.

        If node is join node then update also join specification.
        """
        FDNode.on_update(self, affine)

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
