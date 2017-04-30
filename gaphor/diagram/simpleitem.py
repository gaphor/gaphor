"""
Trivial drawing aids (box, line, ellipse).
"""

from __future__ import absolute_import

from gaphas.item import Element, NW
from gaphas.item import Line as _Line
from gaphas.util import path_ellipse
from six.moves import map
from six.moves import range

from .style import Style


class Line(_Line):
    __style__ = {
        'line-width': 2,
        'line-color': (0, 0, 0, 1),
    }

    def __init__(self, id=None):
        super(Line, self).__init__()
        self.style = Style(Line.__style__)
        self._id = id
        self.fuzziness = 2
        self._handles[0].connectable = False
        self._handles[-1].connectable = False

    id = property(lambda self: self._id, doc='Id')

    def save(self, save_func):
        save_func('matrix', tuple(self.matrix))
        for prop in ('orthogonal', 'horizontal'):
            save_func(prop, getattr(self, prop))
        points = []
        for h in self.handles():
            points.append(tuple(map(float, h.pos)))
        save_func('points', points)

    def load(self, name, value):
        if name == 'matrix':
            self.matrix = eval(value)
        elif name == 'points':
            points = eval(value)
            for x in range(len(points) - 2):
                h = self._create_handle((0, 0))
                self._handles.insert(1, h)
            for i, p in enumerate(points):
                self.handles()[i].pos = p
            self._update_ports()
        elif name == 'horizontal':
            self.horizontal = eval(value)
        elif name == 'orthogonal':
            self._load_orthogonal = eval(value)

    def postload(self):
        if hasattr(self, '_load_orthogonal'):
            self.orthogonal = self._load_orthogonal
            del self._load_orthogonal

    def draw(self, context):
        cr = context.cairo
        style = self.style
        cr.set_line_width(style.line_width)
        cr.set_source_rgba(*style.line_color)
        super(Line, self).draw(context)


class Box(Element):
    """
    A Box has 4 handles (for a start)::
     
    NW +---+ NE
    SW +---+ SE
    """

    __style__ = {
        'border-width': 2,
        'border-color': (0, 0, 0, 1),
        'fill-color': (1, 1, 1, 0),
    }

    def __init__(self, id=None):
        super(Box, self).__init__(10, 10)
        self.style = Style(Box.__style__)
        self._id = id

    id = property(lambda self: self._id, doc='Id')

    def save(self, save_func):
        save_func('matrix', tuple(self.matrix))
        save_func('width', self.width)
        save_func('height', self.height)

    def load(self, name, value):
        if name == 'matrix':
            self.matrix = eval(value)
        elif name == 'width':
            self.width = eval(value)
        elif name == 'height':
            self.height = eval(value)

    def postload(self):
        pass

    def draw(self, context):
        cr = context.cairo
        nw = self._handles[NW]
        style = self.style
        cr.rectangle(nw.pos.x, nw.pos.y, self.width, self.height)
        cr.set_source_rgba(*style.fill_color)
        cr.fill_preserve()
        cr.set_source_rgba(*style.border_color)
        cr.set_line_width(style.border_width)
        cr.stroke()


class Ellipse(Element):
    """
    """

    __style__ = {
        'border-width': 2,
        'border-color': (0, 0, 0, 1),
        'fill-color': (1, 1, 1, 0),
    }

    def __init__(self, id=None):
        super(Ellipse, self).__init__()
        self.style = Style(Ellipse.__style__)
        self._id = id

    id = property(lambda self: self._id, doc='Id')

    def save(self, save_func):
        save_func('matrix', tuple(self.matrix))
        save_func('width', self.width)
        save_func('height', self.height)

    def load(self, name, value):
        if name == 'matrix':
            self.matrix = eval(value)
        elif name == 'width':
            self.width = eval(value)
        elif name == 'height':
            self.height = eval(value)

    def postload(self):
        pass

    def draw(self, context):
        cr = context.cairo
        nw = self._handles[NW]
        style = self.style

        rx = self.width / 2.
        ry = self.height / 2.

        cr.move_to(self.width, ry)
        path_ellipse(cr, rx, ry, self.width, self.height)
        cr.set_source_rgba(*style.fill_color)
        cr.fill_preserve()
        cr.set_source_rgba(*style.border_color)
        cr.set_line_width(style.border_width)
        cr.stroke()

# vim:sw=4:et:ai
