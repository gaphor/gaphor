"""
Basic functionality for canvas line based items on a diagram.
"""
from __future__ import division

from builtins import map
from builtins import range
from past.utils import old_div
from math import atan2, pi

import gaphas

from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.style import get_text_point_at_line
from gaphor.diagram.style import get_text_point_at_line2
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP


class DiagramLine(gaphas.Line, DiagramItem):
    """
    Base class for diagram lines.
    """

    def __init__(self, id=None):
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

        gaphas.Line.pre_update(self, context)
        DiagramItem.pre_update(self, context)

    def post_update(self, context):
        gaphas.Line.post_update(self, context)
        DiagramItem.post_update(self, context)

    def draw(self, context):
        gaphas.Line.draw(self, context)
        DiagramItem.draw(self, context)

    def point(self, pos):
        d1 = gaphas.Line.point(self, pos)
        d2 = DiagramItem.point(self, pos)
        return min(d1, d2)

    def save(self, save_func):
        DiagramItem.save(self, save_func)
        save_func("matrix", tuple(self.matrix))
        for prop in ("orthogonal", "horizontal"):
            save_func(prop, getattr(self, prop))
        points = []
        for h in self.handles():
            points.append(tuple(map(float, h.pos)))
        save_func("points", points)

        canvas = self.canvas
        c = canvas.get_connection(self.head)
        if c:
            save_func("head-connection", c.connected, reference=True)
        c = canvas.get_connection(self.tail)
        if c:
            save_func("tail-connection", c.connected, reference=True)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = eval(value)
        elif name == "points":
            points = eval(value)
            for x in range(len(points) - 2):
                h = self._create_handle((0, 0))
                self._handles.insert(1, h)
            for i, p in enumerate(points):
                self.handles()[i].pos = p

            # Update connection ports of the line. Only handles are saved
            # in Gaphor file therefore ports need to be recreated after
            # handles information is loaded.
            self._update_ports()

        elif name == "orthogonal":
            self._load_orthogonal = eval(value)
        elif name in ("head_connection", "head-connection"):
            self._load_head_connection = value
        elif name in ("tail_connection", "tail-connection"):
            self._load_tail_connection = value
        else:
            DiagramItem.load(self, name, value)

    def _get_sink(self, handle, item):
        """
        Instant port finder.

        This is not the nicest place for such method.
        
        TODO: figure out if part of this functionality can be provided by
        the storage code.
        """
        from gaphas.aspect import ConnectionSink

        hpos = self.canvas.get_matrix_i2i(self, item).transform_point(*handle.pos)
        port = None
        dist = 10e6
        for p in item.ports():
            pos, d = p.glue(hpos)
            if not port or d < dist:
                port = p
                dist = d

        return ConnectionSink(item, port)

    def _postload_connect(self, handle, item):
        """
        Postload connect method.
        """
        from gaphas.aspect import Connector

        connector = Connector(self, handle)

        sink = self._get_sink(handle, item)

        connector.connect(sink)

    def postload(self):
        if hasattr(self, "_load_orthogonal"):
            # Ensure there are enough handles
            if self._load_orthogonal and len(self._handles) < 3:
                p0 = self._handles[-1].pos
                self._handles.insert(1, self._create_handle(p0))
            self.orthogonal = self._load_orthogonal
            del self._load_orthogonal

        # First update matrix and solve constraints (NE and SW handle are
        # lazy and are resolved by the constraint solver rather than set
        # directly.
        self.canvas.update_matrix(self)
        self.canvas.solver.solve()

        if hasattr(self, "_load_head_connection"):
            self._postload_connect(self.head, self._load_head_connection)
            del self._load_head_connection

        if hasattr(self, "_load_tail_connection"):
            self._postload_connect(self.tail, self._load_tail_connection)
            del self._load_tail_connection

        DiagramItem.postload(self)

    def _get_middle_segment(self):
        """
        Get middle line segment.
        """
        handles = self._handles
        m = old_div(len(handles), 2)
        assert m - 1 >= 0 and m < len(handles)
        return handles[m - 1], handles[m]

    def _get_center_pos(self, inverted=False):
        """
        Return position in the centre of middle segment of a line. Angle of
        the middle segment is also returned.
        """
        h0, h1 = self._get_middle_segment()
        pos = old_div((h0.pos.x + h1.pos.x), 2), old_div((h0.pos.y + h1.pos.y), 2)
        angle = atan2(h1.pos.y - h0.pos.y, h1.pos.x - h0.pos.x)
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
        "name-align": (ALIGN_CENTER, ALIGN_TOP),
        "name-padding": (5, 5, 5, 5),
        "name-outside": True,
        "name-align-str": None,
    }

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        self._name = self.add_text(
            "name",
            style={
                "text-align": self.style.name_align,
                "text-padding": self.style.name_padding,
                "text-outside": self.style.name_outside,
                "text-align-str": self.style.name_align_str,
                "text-align-group": "stereotype",
            },
            editable=True,
        )
        self.watch("subject<NamedElement>.name", self.on_named_element_name)

    def postload(self):
        super(NamedLine, self).postload()
        self.on_named_element_name(None)

    def on_named_element_name(self, event):
        self._name.text = self.subject and self.subject.name or ""
        self.request_update()


# vim:sw=4:et:ai
