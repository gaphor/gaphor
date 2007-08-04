"""
Basic functionality for canvas line based items on a diagram.
"""

import itertools

import gaphas
from gaphas.util import text_extents, text_align
from diagramitem import DiagramItem
from interfaces import IConnect

from gaphor.diagram.style import get_text_point_at_line, \
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
            h = self.head

            adapter.connect(h, float(h.x), float(h.y))
            del self._load_head_connection

        if hasattr(self, '_load_tail_connection'):
            adapter = component.queryMultiAdapter((self._load_tail_connection, self), IConnect)
            assert adapter, 'No IConnect adapter to connect %s to %s' % (self._load_tail_connection, self)
            h = self.tail

            adapter.connect(h, float(h.x), float(h.y))
            del self._load_tail_connection
        LineItem.postload(self)


    def text_align(self, extents, align, padding, outside):
        handles = self._handles
        halign, valign = align

        if halign == ALIGN_LEFT:
            p1 = handles[0].pos
            p2 = handles[-1].pos
        elif halign == ALIGN_CENTER:
            m = len(handles) / 2
            assert m - 1 >= 0 and m < len(handles)
            p1 = handles[m - 1].pos
            p2 = handles[m].pos
            x0 = (p1[0] + p2[0]) / 2.0
            y0 = (p1[1] + p2[1]) / 2.0
            p1 = (x0, y0)
            p2 = (x0, y0)
        elif halign == ALIGN_RIGHT:
            p1 = handles[-1].pos
            p2 = handles[-2].pos

        x, y = get_text_point_at_line(extents, p1, p2, align, padding)

        return x, y




class NamedLine(DiagramLine):
    __namedelement__ = True

    __style__ = {
            'name-align': (ALIGN_CENTER, ALIGN_TOP),
            'name-padding': (5, 5, 5, 5),
            'name-outside': True,
    }



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
