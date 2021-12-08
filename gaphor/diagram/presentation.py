from __future__ import annotations

import ast
from dataclasses import replace
from math import atan2

import gaphas
from gaphas.connector import ConnectionSink
from gaphas.connector import Connector as ConnectorAspect
from gaphas.connector import Handle
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.solver.constraint import BaseConstraint

from gaphor.core.modeling.diagram import Diagram
from gaphor.core.modeling.event import RevertibeEvent
from gaphor.core.modeling.presentation import Presentation, S
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import Style, merge_styles
from gaphor.diagram.shapes import stroke
from gaphor.diagram.text import TextAlign, text_point_at_line
from gaphor.i18n import gettext


class Named:
    """Marker for any NamedElement presentations."""


class Classified(Named):
    """Marker for Classifier presentations."""


def from_package_str(item):
    """Display name space info when it is different, then diagram's or parent's
    namespace."""
    subject = item.subject
    diagram = item.diagram

    if not (subject and diagram):
        return False

    namespace = subject.namespace
    parent = item.parent

    # if there is a parent (i.e. interaction)
    if parent and parent.subject and parent.subject.namespace is not namespace:
        return False

    return (
        gettext("(from {namespace})").format(namespace=namespace.name)
        if namespace is not item.diagram.owner
        else ""
    )


def postload_connect(item: gaphas.Item, handle: gaphas.Handle, target: gaphas.Item):
    """Helper function: when loading a model, handles should be connected as
    part of the `postload` step.

    This function finds a suitable spot on the `target` item to connect
    the handle to.
    """
    connector = ConnectorAspect(item, handle, item.diagram.connections)
    sink = ConnectionSink(target, distance=1e4)
    connector.connect(sink)


class HandlePositionEvent(RevertibeEvent):

    requires_transaction = False

    def __init__(self, element, index, old_value):
        super().__init__(element)
        self.index = index
        self.old_value = old_value

    def revert(self, target):
        target.handles()[self.index].pos = self.old_value
        target.request_update()


class HandlePositionUpdate:
    def watch_handle(self, handle):
        handle.pos.add_handler(self._on_handle_position_update)

    def remove_watch_handle(self, handle):
        handle.pos.remove_handler(self._on_handle_position_update)

    def _on_handle_position_update(self, position, old):
        for index, handle in enumerate(self.handles()):  # type: ignore[attr-defined]
            if handle.pos is position:
                break
        else:
            return
        self.handle(HandlePositionEvent(self, index, old))  # type: ignore[attr-defined]


# Note: the official documentation is using the terms "Shape" and "Edge" for element and line.


class ElementPresentation(gaphas.Element, HandlePositionUpdate, Presentation[S]):
    """Presentation for Gaphas Element (box-like) items.

    To create a shape (boxes, text), assign a shape to `self.shape`. If
    the shape can change, for example, because styling needs to change,
    implement the method `update_shapes()` and set self.shape there.
    """

    _port_sides = ("top", "right", "bottom", "left")

    def __init__(self, diagram: Diagram, id=None, shape=None, width=100, height=50):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id, width=width, height=height)  # type: ignore[call-arg]
        self._shape = shape
        for handle in self.handles():
            self.watch_handle(handle)

        diagram.connections.add_constraint(
            self, MinimalValueConstraint(self.min_width, width)
        )
        diagram.connections.add_constraint(
            self, MinimalValueConstraint(self.min_height, height)
        )

    def port_side(self, port):
        return self._port_sides[self._ports.index(port)]

    def _set_shape(self, shape):
        self._shape = shape
        self.request_update()

    shape = property(lambda s: s._shape, _set_shape)

    def update_shapes(self, event=None):
        """Updating the shape configuration, e.g. when extra elements have to
        be drawn or when styling changes."""

    def update(self, context):
        if not self.shape:
            self.update_shapes()
        if self.shape:
            self.min_width, self.min_height = self.shape.size(context)

    def draw(self, context):
        x, y = self.handles()[0].pos
        cairo = context.cairo
        cairo.translate(x, y)
        self._shape.draw(
            context,
            Rectangle(0, 0, self.width, self.height),
        )

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("width", self.width)
        save_func("height", self.height)
        super().save(save_func)

    def load(self, name, value):
        if name == "width":
            self.width = ast.literal_eval(value)
        elif name == "height":
            self.height = ast.literal_eval(value)
        else:
            super().load(name, value)

    def postload(self):
        super().postload()
        self.update_shapes()


class MinimalValueConstraint(BaseConstraint):
    def __init__(self, var, min):
        super().__init__(var)
        self._min = min

    def solve_for(self, var):
        min = self._min
        if var is min:
            return
        var.value = max(var.value, min)


class LinePresentation(gaphas.Line, HandlePositionUpdate, Presentation[S]):
    def __init__(
        self,
        diagram: Diagram,
        id=None,
        style: Style = {},
        shape_head=None,
        shape_middle=None,
        shape_tail=None,
    ):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id)  # type: ignore[call-arg]

        self.style = style
        self.shape_head = shape_head
        self.shape_middle = shape_middle
        self.shape_tail = shape_tail

        self.fuzziness = 2
        self._shape_head_rect = None
        self._shape_middle_rect = None
        self._shape_tail_rect = None
        self.watch("orthogonal", self._on_orthogonal).watch(
            "horizontal", self._on_horizontal
        )
        self.watch_handle(self.head)
        self.watch_handle(self.tail)

    head = property(lambda self: self._handles[0])
    tail = property(lambda self: self._handles[-1])

    orthogonal: attribute[int] = attribute("orthogonal", int, 0)
    horizontal: attribute[int] = attribute("horizontal", int, 0)

    @property
    def middle_shape_size(self) -> Rectangle:
        return self._shape_middle_rect

    def insert_handle(self, index: int, handle: Handle) -> None:
        super().insert_handle(index, handle)
        self.watch_handle(handle)

    def remove_handle(self, handle: Handle) -> None:
        self.remove_watch_handle(handle)
        super().remove_handle(handle)

    def update_shape_bounds(self, context):
        def shape_bounds(shape, align):
            if shape:
                size = shape.size(context)
                x, y = text_point_at_line(points, size, align)
                return Rectangle(x, y, *size)

        points = [h.pos for h in self.handles()]
        self._shape_head_rect = shape_bounds(self.shape_head, TextAlign.LEFT)
        self._shape_middle_rect = shape_bounds(self.shape_middle, TextAlign.CENTER)
        self._shape_tail_rect = shape_bounds(self.shape_tail, TextAlign.RIGHT)

    def point(self, x, y):
        """Given a point (x, y) return the distance to the diagram item."""
        d0 = super().point(x, y)
        ds = [
            distance_rectangle_point(shape, (x, y))
            for shape in (
                self._shape_head_rect,
                self._shape_middle_rect,
                self._shape_tail_rect,
            )
            if shape
        ]
        return min(d0, *ds) if ds else d0

    def draw(self, context):
        def draw_line_end(end_handle, second_handle, draw):
            pos, p1 = end_handle.pos, second_handle.pos
            angle = atan2(p1.y - pos.y, p1.x - pos.x)
            cr.save()
            try:
                cr.translate(*pos)
                cr.rotate(angle)
                draw(context)
            finally:
                cr.restore()

        style = merge_styles(context.style, self.style)
        context = replace(context, style=style)

        self.update_shape_bounds(context)
        cr = context.cairo

        handles = self._handles
        draw_line_end(handles[0], handles[1], self.draw_head)

        for h in self._handles[1:-1]:
            cr.line_to(*h.pos)

        draw_line_end(handles[-1], handles[-2], self.draw_tail)

        stroke(context)

        for shape, rect in (
            (self.shape_head, self._shape_head_rect),
            (self.shape_middle, self._shape_middle_rect),
            (self.shape_tail, self._shape_tail_rect),
        ):
            if shape:
                shape.draw(context, rect)

    def save(self, save_func):
        def save_connection(name, handle):
            c = self._connections.get_connection(handle)
            if c:
                save_func(name, c.connected)

        super().save(save_func)
        save_func("matrix", tuple(self.matrix))
        points = [tuple(map(float, h.pos)) for h in self.handles()]
        save_func("points", points)

        save_connection("head-connection", self.head)
        save_connection("tail-connection", self.tail)

    def load(self, name, value):
        if name == "points":
            points = ast.literal_eval(value)
            for _ in range(len(points) - 2):
                h = Handle((0, 0))
                self._handles.insert(1, h)
                self.watch_handle(h)
            for i, p in enumerate(points):
                self.handles()[i].pos = p
            self._update_ports()
        elif name in ("head_connection", "head-connection"):
            self._load_head_connection = value
        elif name in ("tail_connection", "tail-connection"):
            self._load_tail_connection = value
        else:
            super().load(name, value)

    def postload(self):
        super().postload()

        if self.orthogonal:
            self._on_orthogonal(None)

        if hasattr(self, "_load_head_connection"):
            postload_connect(self, self.head, self._load_head_connection)
            assert self._connections.get_connection(self.head)
            del self._load_head_connection

        if hasattr(self, "_load_tail_connection"):
            postload_connect(self, self.tail, self._load_tail_connection)
            assert self._connections.get_connection(self.tail)
            del self._load_tail_connection

    def _on_orthogonal(self, _event):
        if self.orthogonal and len(self.handles()) < 3:
            raise ValueError("Can't set orthogonal line with less than 3 handles")
        self.update_orthogonal_constraints(self.orthogonal)

    def _on_horizontal(self, _event):
        self.update_orthogonal_constraints(self.orthogonal)
