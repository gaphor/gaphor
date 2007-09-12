    """
    Basic functionality for canvas line based items on a diagram.
    """

    from math import atan2, pi

import gaphas
from gaphas.util import text_extents, text_align
from diagramitem import DiagramItem
from interfaces import IConnect

from gaphor.diagram.style import get_text_point_at_line, \
    get_text_point_at_line2, \
    ALIGN_CENTER, ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP

class LineItem(gaphas.Line, DiagramItem):
    """
    Base class for diagram lines.
    """

    def __init__(self, id = None):
        gaphas.Line.__init__(self)
        DiagramItem.__init__(self, id)
        self.fuzziness = 2

    head = property(lambda self: self._handles[0])
    tail = property(lambda self: self._handles[-1])


    def setup_canvas(self):
        gaphas.Line.setup_canvas()
        self.register_handlers()


    def teardown_canvas(self):
        gaphas.Line.teardown_canvas()
        self.unregister_handlers()


    def pre_update(self, context):
        # first, update stereotype to know its text
        self.update_stereotype()

        #super(LineItem, self).pre_update(context)
        gaphas.Line.pre_update(self, context)
        DiagramItem.pre_update(self, context)


    def post_update(self, context):
        #super(LineItem, self).update(context)
        gaphas.Line.post_update(self, context)
        DiagramItem.post_update(self, context)


    def draw(self, context):
        #super(LineItem, self).draw(context)
        gaphas.Line.draw(self, context)
        DiagramItem.draw(self, context)


    def point(self, x, y):
        d1 = gaphas.Line.point(self, x, y)
        d2 = DiagramItem.point(self, x, y)
        return min(d1, d2)


class DiagramLine(LineItem):
    """
    Gaphor lines. This line is serializable and has a popup
    menu.

    TODO: put serializability and popup in separate adapters.
    """

    def save (self, save_func):
        LineItem.save(self, save_func)
        save_func('matrix', tuple(self.matrix))
        for prop in ('orthogonal', 'horizontal'):
            save_func(prop, getattr(self, prop))
        points = [ ]
        for h in self.handles():
            points.append(tuple(map(float, h.pos)))
        save_func('points', points)
        c = self.head.connected_to
        if c:
            save_func('head-connection', c, reference=True)
        c = self.tail.connected_to
        if c:
            save_func('tail-connection', c, reference=True)

    def load (self, name, value):
        if name == 'matrix':
            self.matrix = eval(value)
        elif name == 'points':
            points = eval(value)
            for x in xrange(len(points) - 2):
                self.split_segment(0)
            for i, p in enumerate(points):
                self.handles()[i].pos = p
        elif name == 'orthogonal':
            self._load_orthogonal = eval(value)
        elif name in ('head_connection', 'head-connection'):
            self._load_head_connection = value
        elif name in ('tail_connection', 'tail-connection'):
            self._load_tail_connection = value
        else:
            LineItem.load(self, name, value)

    def postload(self):
        # Ohoh, need the IConnect adapters here
        from zope import component
        if hasattr(self, '_load_orthogonal'):
            self.orthogonal = self._load_orthogonal
            del self._load_orthogonal

        # First update matrix and solve constraints (NE and SW handle are
        # lazy and are resolved by the constraint solver rather than set
        # directly.
        #self.canvas.update_matrix(self)
        #self.canvas.solver.solve()

        if hasattr(self, '_load_head_connection'):
            adapter = component.queryMultiAdapter((self._load_head_connection, self), IConnect)
            assert adapter, 'No IConnect adapter to connect %s to %s' % (self._load_head_connection, self)

            adapter.connect(self.head)
            del self._load_head_connection

        if hasattr(self, '_load_tail_connection'):
            adapter = component.queryMultiAdapter((self._load_tail_connection, self), IConnect)
            assert adapter, 'No IConnect adapter to connect %s to %s' % (self._load_tail_connection, self)

            adapter.connect(self.tail)
            del self._load_tail_connection
        LineItem.postload(self)


    def _get_middle_segment(self):
        """
        Get middle line segment.
        """
        handles = self._handles
        m = len(handles) / 2
        assert m - 1 >= 0 and m < len(handles)
        return handles[m - 1], handles[m]


    def _get_center_pos(self, inverted=False):
        """
        Return position in the centre of middle segment of a line. Angle of
        the middle segment is also returned.
        """
        h0, h1 = self._get_middle_segment()
        pos = (h0.x + h1.x) / 2, (h0.y + h1.y) / 2
        angle = atan2(h1.y - h0.y, h1.x - h0.x)
        if inverted:
            angle += pi
        return pos, angle


    def text_align(self, extents, align, padding, outside):
        handles = self._handles
        halign, valign = align

        if halign == ALIGN_LEFT:
            p1 = handles[0].pos
            p2 = handles[-1].pos
            x, y = get_text_point_at_line(extents, p1, p2, align, padding)

        elif halign == ALIGN_CENTER:
            h0, h1 = self._get_middle_segment()
            p1 = h0.pos
            p2 = h1.pos
            x, y = get_text_point_at_line2(extents, p1, p2, align, padding)
        elif halign == ALIGN_RIGHT:
            p1 = handles[-1].pos
            p2 = handles[-2].pos

            x, y = get_text_point_at_line(extents, p1, p2, align, padding)

        return x, y




class NamedLine(DiagramLine):

    __style__ = {
            'name-align': (ALIGN_CENTER, ALIGN_TOP),
            'name-padding': (5, 5, 5, 5),
            'name-outside': True,
            'name-align-str': None,
    }

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        obj._name = obj.add_text('name', style={
                    'text-align': self.style.name_align,
                    'text-padding': self.style.name_padding,
                    'text-outside': self.style.name_outside,
                    'text-align-str': self.style.name_align_str,
                    'text-align-group': 'stereotype',
                }, editable=True)
        self.add_watch(UML.NamedElement.name, self.on_named_element_name)


    def on_named_element_name(self, event):
        self._name.text = subject.name
        self.request_update()


class FreeLine(LineItem):
    """
    TODO: get rid of this one.

    A line with disabled last handle. This allows to create diagram items,
    which have one or more additional lines.

    Last handle is usually attached to a point of diagram item. This point
    is called main point.
    """
    def __init__(self, id = None, mpt = None):
        LineItem.__init__(self, id)

        # expose first handle
        self._handle = self.handles[0]

        # disable last handle, it should be in main point
        h = self.handles[-1]
        h.props.movable = False
        h.props.connectable = False
        h.props.visible = False

        self._main_point = mpt

        if self._main_point is None:
            self._main_point = 0, 0


    def on_update(self, affine):
        self.handles[-1].set_pos_i(*self._main_point)
        self._handle.set_pos_i(*self._handle.get_pos_i()) # really strange, but we have to do this

        LineItem.on_update(self, affine)

# vim:sw=4:et
