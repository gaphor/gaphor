"""
Basic functionality for canvas line based items on a diagram.
"""

from math import atan2, pi

import gaphas
from gaphor import UML
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
        gaphas.Line.setup_canvas(self)
        self.register_handlers()


    def teardown_canvas(self):
        gaphas.Line.teardown_canvas(self)
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


    def point(self, pos):
        d1 = gaphas.Line.point(self, pos)
        d2 = DiagramItem.point(self, pos)
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
                h = self._create_handle((0, 0))
                self._handles.insert(1, h)
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


    def _connect(self, handle, item):
        # we need connection tool, here;
        # can we move that to storage module?
        from gaphor.ui.diagramtools import ConnectHandleTool
        tool = ConnectHandleTool()

        port = tool.find_port(self, handle, item)
        tool.connect_handle(self, handle, item, port)
        tool.post_connect(self, handle, item, port)


    def postload(self):
        if hasattr(self, '_load_orthogonal'):
            self.orthogonal = self._load_orthogonal
            del self._load_orthogonal

        # First update matrix and solve constraints (NE and SW handle are
        # lazy and are resolved by the constraint solver rather than set
        # directly.
        #self.canvas.update_matrix(self)
        #self.canvas.solver.solve()

        if hasattr(self, '_load_head_connection'):
            self._connect(self.head, self._load_head_connection)
            del self._load_head_connection

        if hasattr(self, '_load_tail_connection'):
            self._connect(self.tail, self._load_tail_connection)
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
        self._name = self.add_text('name', style={
                    'text-align': self.style.name_align,
                    'text-padding': self.style.name_padding,
                    'text-outside': self.style.name_outside,
                    'text-align-str': self.style.name_align_str,
                    'text-align-group': 'stereotype',
                }, editable=True)
        self.add_watch(UML.NamedElement.name, self.on_named_element_name)


    def on_named_element_name(self, event):
        if self.subject and (event is None or self.subject is event.element):
            self._name.text = self.subject.name
            self.request_update()

# vim:sw=4:et
