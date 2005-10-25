"""InitialNode and ActivityFinalNode.
"""
# vim:sw=4:et

import math
import itertools

import gobject
import pango

import diacanvas
from gaphor import UML
from gaphor.diagram import initialize_item
from elementitem import ElementItem
from nameditem import NamedItem, SimpleNamedItem


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



class ForkNodeItem(FDNode):
    WIDTH  =  6.0
    HEIGHT = 45.0

    def __init__(self, id=None):
        FDNode.__init__(self, id)
        self._rect = diacanvas.shape.Path()
        self._rect.rectangle((0, 0), (self.WIDTH, self.HEIGHT))
        self._rect.set_fill_color(diacanvas.color(0,0,0))
        self._rect.set_fill(diacanvas.shape.FILL_SOLID)

        self.set(width = self.WIDTH, height = self.HEIGHT)
        self.handles[0].set_property('movable', True)
        self.handles[3].set_property('movable', True)


    def on_update(self, affine):
        FDNode.on_update(self, affine)
        self._rect.rectangle((0, 0), (self.width, self.height))


    def on_shape_iter(self):
        return iter([self._rect])



class ObjectNodeItem(SimpleNamedItem):
    FONT = 'sans 10'

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
        SimpleNamedItem.__init__(self, id)

        self.show_ordering = False

        self._ordering = diacanvas.shape.Text()
        self._ordering.set_font_description(pango.FontDescription(self.FONT))
        self._ordering.set_alignment(pango.ALIGN_CENTER)
        self._ordering.set_markup(False)


    def save(self, save_func):
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
        return diacanvas.shape.Path()


    def draw_border(self):
        self._border.rectangle((0, 0), (self.width, self.height))


    def on_update(self, affine):
        SimpleNamedItem.on_update(self, affine)
        if self.subject:
            self._ordering.set_text('{ ordering = %s }' % self.subject.ordering)
        else:
            self._ordering.set_text('')

        # center ordering below border
        width, height = self._ordering.to_pango_layout(True).get_pixel_size()
        x = (self.width - width) / 2
        self._ordering.set_pos((x, self.height + 10))
        self._ordering.set_max_width(width)
        self._ordering.set_max_height(height)

        if self.show_ordering:
            self.set_bounds((min(0, x), 0,
                max(self.width, width), self.height + 10 + height))


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
