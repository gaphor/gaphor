"""
Activity nodes.
"""
# vim:sw=4:et

import math
import itertools

import gobject
import pango

import diacanvas
from gaphor import UML
from gaphor import resource
from gaphor.diagram import initialize_item, TextElement
from elementitem import ElementItem
from nameditem import NamedItem, SimpleNamedItem, SideNamedItem
from gaphor.diagram.groupable import GroupBase, Groupable


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
            h.set_property('movable', False)



class InitialNodeItem(ActivityNodeItem, SideNamedItem):
    """
    Representation of initial node. Initial node has name which is put near
    top-left side of node.
    """

    __metaclass__ = Groupable
    RADIUS = 10

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        SideNamedItem.__init__(self)
        r = self.RADIUS
        d = r * 2
        self._circle = diacanvas.shape.Ellipse()
        self._circle.ellipse((r, r), d, d)
        self._circle.set_line_width(0.01)
        self._circle.set_fill(diacanvas.shape.FILL_SOLID)
        self._circle.set_fill_color(diacanvas.color(0, 0, 0, 255))
        self.set(width=d, height=d)


    def on_subject_notify(self, pspec, notifiers = ()):
        ActivityNodeItem.on_subject_notify(self, pspec, notifiers)
        self._name.subject = self.subject
        self.request_update()


    def on_update(self, affine):
        ActivityFinalNodeItem.on_update(self, affine)
        SideNamedItem.on_update(self, affine)


    def on_shape_iter(self):
        return iter([self._circle])



class ActivityFinalNodeItem(ActivityNodeItem):
    """
    Representation of activity final node.
    """
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
    """
    Representation of flow final node.
    """
    RADIUS = 10

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
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
        'combined': (gobject.TYPE_BOOLEAN, 'combined', '', 1,
                gobject.PARAM_READWRITE),
    }

    def __init__(self, id):
        ActivityNodeItem.__init__(self, id)
        self.combined = False

    def save(self, save_func):
        self.save_property(save_func, 'combined')
        ActivityNodeItem.save(self, save_func)

    def do_set_property(self, pspec, value):
        if pspec.name == 'combined':
            self.preserve_property('combined')
            self.combined = value
        else:
            ActivityNodeItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'combined':
            return self.combined
        else:
            return ActivityNodeItem.do_get_property(self, pspec)



class DecisionNodeItem(FDNode):
    """
    Representation of decision or merge node.
    """
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

    __metaclass__ = Groupable

    WIDTH  =  6.0
    HEIGHT = 45.0

    def __init__(self, id=None):
        GroupBase.__init__(self, {
            '_join_spec': TextElement('value', '{ joinSpec = %s }'),
        })
        FDNode.__init__(self, id)
        self._rect = diacanvas.shape.Path()
        self._rect.rectangle((0, 0), (self.WIDTH, self.HEIGHT))
        self._rect.set_fill_color(diacanvas.color(0,0,0))
        self._rect.set_fill(diacanvas.shape.FILL_SOLID)

        self.set(width = self.WIDTH, height = self.HEIGHT)
        self.handles[0].set_property('movable', True)
        self.handles[3].set_property('movable', True)


    def on_update(self, affine):
        """
        Update fork/join node.

        If node is join node then update also join specification.
        """
        FDNode.on_update(self, affine)
        self._rect.rectangle((0, 0), (self.width, self.height))

        if isinstance(self.subject, UML.JoinNode) and self.subject.joinSpec == 'and':
            self._join_spec.set_text('')

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
            self.subject.joinSpec = factory.create(UML.LiteralSpecification)
            self._join_spec.subject = self.subject.joinSpec
        else:
            self._join_spec.subject = None
        self.request_update()


    def on_shape_iter(self):
        return iter([self._rect])



class ObjectNodeItem(SimpleNamedItem, GroupBase):
    """
    Representation of object node. Object node is ordered and has upper bound
    specification.

    Ordering information can be hidden by user.
    """

    __metaclass__ = Groupable

    FONT = 'sans 10'
    MARGIN = 10

    node_popup_menu = (
        'separator',
        'Ordering', ('ObjectNodeOrderingVisibilty',
            'separator',
            'ObjectNodeOrderingUnordered',
            'ObjectNodeOrderingOrdered',
            'ObjectNodeOrderingLIFO',
            'ObjectNodeOrderingFIFO')
    )

    __gproperties__ = {
        'show-ordering': (gobject.TYPE_BOOLEAN, 'show ordering', '', 1,
                gobject.PARAM_READWRITE),
    }

    def __init__(self, id = None):
        GroupBase.__init__(self, {
            '_upper_bound': TextElement('value', '{ upperBound = %s }'),
        })
        SimpleNamedItem.__init__(self, id)

        self.show_ordering = False

        self._ordering = diacanvas.shape.Text()
        self._ordering.set_font_description(pango.FontDescription(self.FONT))
        self._ordering.set_alignment(pango.ALIGN_CENTER)
        self._ordering.set_markup(False)


    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Detect subject changes. If subject is set then set upper bound text
        element subject.
        """
        SimpleNamedItem.on_subject_notify(self, pspec, notifiers)
        if self.subject:
            factory = resource(UML.ElementFactory)
            self.subject.upperBound = factory.create(UML.LiteralSpecification)
            self._upper_bound.subject = self.subject.upperBound
        else:
            self._upper_bound.subject = None
        self.request_update()


    #
    # fixme: saving and getting properties, cannot we automate this?
    #
    def save(self, save_func):
        """
        Save visibility of object node ordering.
        """
        self.save_property(save_func, 'show-ordering')
        SimpleNamedItem.save(self, save_func)


    def do_set_property(self, pspec, value):
        if pspec.name == 'show-ordering':
            self.preserve_property('show-ordering')
            self.show_ordering = value
        else:
            SimpleNamedItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name == 'show-ordering':
            return self.show_ordering
        else:
            return SimpleNamedItem.do_get_property(self, pspec)


    def get_popup_menu(self):
        return self.popup_menu + self.node_popup_menu


    def set_show_ordering(self, value):
        """
        Set visibility of object node ordering and request update.
        """
        self.show_ordering = value
        self.request_update()


    def set_ordering(self, ordering):
        """
        Set ordering of object node.
        """
        self.subject.ordering = ordering
        self.request_update()


    def get_ordering(self):
        """
        Determine ordering of object node.
        """
        return self.subject.ordering


    def get_border(self):
        """
        Return border of simple named item.
        """
        return diacanvas.shape.Path()


    def draw_border(self):
        """
        Draw border of simple named item.
        """
        self._border.rectangle((0, 0), (self.width, self.height))


    def on_update(self, affine):
        """
        Update object node, its ordering and upper bound specification.
        """
        SimpleNamedItem.on_update(self, affine)

        if self.subject:
            self._ordering.set_text('{ ordering = %s }' % self.subject.ordering)

            if self.subject.upperBound.value == '*':
                self._upper_bound.set_text('')

        else:
            self._ordering.set_text('')

        # 
        # object ordering
        #
        if self.show_ordering:
            # center ordering below border
            ord_width, ord_height = self._ordering.to_pango_layout(True).get_pixel_size()
            x = (self.width - ord_width) / 2
            self._ordering.set_pos((x, self.height + self.MARGIN))

            self._ordering.set_max_width(ord_width)
            self._ordering.set_max_height(ord_height)

            self.set_bounds((min(0, x), 0,
                max(self.width, ord_width), self.height + self.MARGIN + ord_height))
        else:
            ord_width, ord_height = 0, 0

        #
        # upper bound
        #
        ub_width, ub_height = self._upper_bound.get_size()
        x = (self.width - ub_width) / 2
        y = self.height + ord_height + self.MARGIN
        self._upper_bound.update_label(x, y)

        GroupBase.on_update(self, affine)


    def on_shape_iter(self):
        it = SimpleNamedItem.on_shape_iter(self)
        if self.show_ordering:
            return itertools.chain(it, iter([self._ordering]))
        else:
            return it



gobject.type_register(FDNode)
initialize_item(ActivityNodeItem)
initialize_item(InitialNodeItem, UML.InitialNode)
initialize_item(ActivityFinalNodeItem, UML.ActivityFinalNode)
initialize_item(FlowFinalNodeItem, UML.FlowFinalNode)
initialize_item(DecisionNodeItem, UML.DecisionNode)
initialize_item(ForkNodeItem, UML.ForkNode)
initialize_item(ObjectNodeItem, UML.ObjectNode)
