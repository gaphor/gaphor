from __future__ import annotations

from collections.abc import Iterator
from math import atan2

import gaphas
from gaphas.connector import ConnectionSink, Handle, LinePort, Position
from gaphas.connector import Connector as ConnectorAspect
from gaphas.constraint import constraint
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.solver.constraint import BaseConstraint

from gaphor.core.modeling.diagram import Diagram, DrawContext
from gaphor.core.modeling.element import Id
from gaphor.core.modeling.event import AttributeUpdated, RevertibleEvent
from gaphor.core.modeling.presentation import Presentation, S, literal_eval
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.shapes import CssNode, Shape, Text, stroke, traverse_css_nodes
from gaphor.diagram.text import TextAlign, middle_segment, text_point_at_line

DEFAULT_HEIGHT = 50
DEFAULT_WIDTH = 100


class Named:
    """Marker for any presentations with a name."""


class Valued:
    """Marker for any element that has a value."""


class Classified(Named):
    """Marker for Classifier presentations."""


def text_name(item: Presentation):
    """An item subject's `name` field."""
    return CssNode(
        "name",
        item.subject,
        Text(text=lambda: item.subject and item.subject.name or ""),
    )


def connect(item: gaphas.Item, handle: gaphas.Handle, target: gaphas.Item):
    connector = ConnectorAspect(item, handle, item.diagram.connections)
    sink = ConnectionSink(target, distance=float("inf"))
    connector.connect(sink)


def postload_connect(item: gaphas.Item, handle: gaphas.Handle, target: gaphas.Item):
    """Reconnect handles after model loading.

    When loading a model, handles should be connected as part of the `postload` step.

    This function finds a suitable spot on the `target` item to connect the `handle` to.
    """
    target.postload()
    item.diagram.update({item, target})
    connector = ConnectorAspect(item, handle, item.diagram.connections)
    sink = ConnectionSink(target, distance=float("inf"))
    connector.glue(sink)
    connector.connect_handle(sink)


class HandlePositionEvent(RevertibleEvent):
    def __init__(self, element, handle, old_value):
        super().__init__(element)
        self.handle_index = element.handles().index(handle)
        self.old_value = old_value
        self.new_value = handle.pos.tuple()

    def revert(self, target):
        target.handles()[self.handle_index].pos = self.old_value
        target.request_update()


class HandlePositionUpdate:
    def watch_handle(self, handle):
        handle.pos.add_handler(self._on_handle_position_update)

    def remove_watch_handle(self, handle):
        handle.pos.remove_handler(self._on_handle_position_update)

    def _on_handle_position_update(self, position, old):
        for handle in self.handles():  # type: ignore[attr-defined]
            if handle.pos is position:
                self.handle(HandlePositionEvent(self, handle, old))  # type: ignore[attr-defined]
                break


# Note: the official documentation is using the terms "Shape" and "Edge" for element and line.


class ElementPresentation(gaphas.Element, HandlePositionUpdate, Presentation[S]):
    """Presentation for Gaphas Element (box-like) items.

    To create a shape (boxes, text), assign a shape to `self.shape`. If
    the shape can change, for example, because styling needs to change,
    implement the method `update_shapes()` and set self.shape there.
    """

    _port_sides = ("top", "right", "bottom", "left")

    def __init__(
        self,
        diagram: Diagram,
        id: Id | None = None,
        shape: Shape | None = None,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
    ):
        super().__init__(
            connections=diagram.connections,
            diagram=diagram,
            id=id,
            width=width,
            height=height,
        )  # type: ignore[call-arg]
        self._shape = shape
        for handle in self.handles():
            self.watch_handle(handle)

        diagram.connections.add_constraint(
            self,
            MinimalValueConstraint(self.min_width, width),  # type: ignore[has-type]
        )
        diagram.connections.add_constraint(
            self,
            MinimalValueConstraint(self.min_height, height),  # type: ignore[has-type]
        )

    def port_side(self, port):
        return self._port_sides[self._ports.index(port)]

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        self._shape = shape
        self.request_update()

    def update_shapes(self, event=None):
        """Updating the shape configuration, e.g. when extra elements have to
        be drawn or when styling changes."""

    def update(self, context):
        if not self._shape:
            self.update_shapes()
        if self._shape:
            self.min_width, self.min_height = self._shape.size(
                context, bounding_box=Rectangle(0, 0, self.width, self.height)
            )

    def css_nodes(self) -> Iterator[CssNode]:
        return traverse_css_nodes(self._shape) if self._shape else iter(())

    def draw(self, context):
        x, y = self.handles()[0].pos
        cairo = context.cairo
        cairo.translate(x, y)
        if self._shape:
            self._shape.draw(
                context,
                Rectangle(0, 0, self.width, self.height),
            )

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("top-left", tuple(map(float, self._handles[0].pos)))
        save_func("width", self.width)
        save_func("height", self.height)
        super().save(save_func)

    def load(self, name, value):
        if name == "top-left":
            pos = literal_eval(value)
            self._handles[0].pos = pos
            # Also adjust bottom-right handle to keep width and height intact
            self._handles[2].pos.x += pos[0]
            self._handles[2].pos.y += pos[1]
        elif name == "width":
            self.width = literal_eval(value)
        elif name == "height":
            self.height = literal_eval(value)
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
        id: Id | None = None,
        shape_head: Shape | None = None,
        shape_middle: Shape | None = None,
        shape_tail: Shape | None = None,
    ):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id)  # type: ignore[call-arg]

        self._shape_head = shape_head
        self._shape_middle = shape_middle
        self._shape_tail = shape_tail

        self.fuzziness = 4
        self._shape_head_rect = None
        self._shape_middle_rect = None
        self._shape_tail_rect = None

        self.watch_handle(self.head)
        self.watch_handle(self.tail)

    orthogonal: attribute[int] = attribute("orthogonal", int, 0)
    horizontal: attribute[int] = attribute("horizontal", int, 0)

    @property
    def head(self):
        return self._handles[0]

    @property
    def tail(self):
        return self._handles[-1]

    @property
    def shape_head(self):
        return self._shape_head

    @property
    def shape_middle(self):
        return self._shape_middle

    @property
    def shape_tail(self):
        return self._shape_tail

    @property
    def middle_shape_size(self) -> Rectangle:
        return self._shape_middle_rect

    def insert_handle(self, index: int, handle: Handle) -> None:
        super().insert_handle(index, handle)
        self.watch_handle(handle)
        self.update_orthogonal_constraints()

    def remove_handle(self, handle: Handle) -> None:
        self.remove_watch_handle(handle)
        super().remove_handle(handle)
        self.update_orthogonal_constraints()

    def update_shape_bounds(self, context):
        def shape_bounds(shape, align):
            if shape:
                size = shape.size(context)
                x, y = text_point_at_line(points, size, align)
                return Rectangle(x, y, *size)

        points = [h.pos for h in self.handles()]
        self._shape_head_rect = shape_bounds(self._shape_head, TextAlign.LEFT)
        self._shape_middle_rect = shape_bounds(self._shape_middle, TextAlign.CENTER)
        self._shape_tail_rect = shape_bounds(self._shape_tail, TextAlign.RIGHT)

    def css_nodes(self) -> Iterator[CssNode]:
        if self._shape_head:
            yield from traverse_css_nodes(self._shape_head)
        if self._shape_middle:
            yield from traverse_css_nodes(self._shape_middle)
        if self._shape_tail:
            yield from traverse_css_nodes(self._shape_tail)

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

    def draw(self, context: DrawContext):
        self.update_shape_bounds(context)
        cr = context.cairo

        handles = self._handles
        draw_line_end(context, handles[0], handles[1], self.draw_head)

        for h in self._handles[1:-1]:
            cr.line_to(*h.pos)

        draw_line_end(context, handles[-1], handles[-2], self.draw_tail)

        stroke(context, fill=False)

        for shape, rect in (
            (self._shape_head, self._shape_head_rect),
            (self._shape_middle, self._shape_middle_rect),
            (self._shape_tail, self._shape_tail_rect),
        ):
            if shape:
                shape.draw(context, rect)

    def save(self, save_func):
        def save_connection(name, handle):
            if c := self._connections.get_connection(handle):
                save_func(name, c.connected)

        super().save(save_func)
        save_func("matrix", tuple(self.matrix))
        points = [tuple(map(float, h.pos)) for h in self.handles()]
        save_func("points", points)

        save_connection("head-connection", self.head)
        save_connection("tail-connection", self.tail)

    def load(self, name, value):
        if name == "points":
            points = literal_eval(value)
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

        if hasattr(self, "_load_head_connection"):
            postload_connect(self, self.head, self._load_head_connection)
            assert self._connections.get_connection(self.head)
            del self._load_head_connection

        if hasattr(self, "_load_tail_connection"):
            postload_connect(self, self.tail, self._load_tail_connection)
            assert self._connections.get_connection(self.tail)
            del self._load_tail_connection

        self.update_orthogonal_constraints()

    def handle(self, event):
        if isinstance(event, AttributeUpdated) and event.property in (
            LinePresentation.horizontal,
            LinePresentation.orthogonal,
        ):
            self.update_orthogonal_constraints()
        super().handle(event)


def get_center_pos(points):
    """Return position in the centre of middle segment of a line.

    Angle of the middle segment is also returned.
    """
    h0, h1 = middle_segment(points)
    pos = (h0.pos.x + h1.pos.x) / 2, (h0.pos.y + h1.pos.y) / 2
    angle = atan2(h1.pos.y - h0.pos.y, h1.pos.x - h0.pos.x)
    return pos, angle


def draw_line_end(context, end_handle, second_handle, draw):
    cr = context.cairo
    pos, p1 = end_handle.pos, second_handle.pos
    angle = atan2(p1.y - pos.y, p1.x - pos.x)
    cr.save()
    try:
        cr.translate(*pos)
        cr.rotate(angle)
        draw(context)
    finally:
        cr.restore()


class AttachedPresentation(HandlePositionUpdate, Presentation[S]):
    """An attached presentation is a base type for all sorts of element-like
    presentations that can be attached to an element.

    An AttachedPresentation has one handle at the center to connect to
    an element.

    E.g. ports, pins and parameter nodes.
    """

    def __init__(
        self,
        diagram: Diagram,
        id: Id | None = None,
        shape: Shape | None = None,
        width=16,
        height=16,
    ):
        super().__init__(diagram, id)
        self._connections = diagram.connections
        self._width_constraints: list[BaseConstraint] = []
        self._height_constraints: list[BaseConstraint] = []
        self._last_connected_side = None
        self._shape = shape

        handle = self._handle = Handle(strength=gaphas.solver.STRONG, connectable=True)
        self.watch_handle(handle)

        rh = width / 2
        rv = height / 2
        top_left = Position(-rh, -rv)
        top_right = Position(rh, -rv)
        bottom_right = Position(rh, rv)
        bottom_left = Position(-rh, rv)

        add = diagram.connections.add_constraint
        add(self, constraint(horizontal=(top_left, top_right)))
        add(self, constraint(horizontal=(bottom_left, bottom_right)))
        add(self, constraint(vertical=(top_left, bottom_left)))
        add(self, constraint(vertical=(top_right, bottom_right)))

        self._corners = [top_left, top_right, bottom_right, bottom_left]

        self._ports = [
            LinePort(top_left, top_right),
            LinePort(top_right, bottom_right),
            LinePort(bottom_right, bottom_left),
            LinePort(bottom_left, top_left),
        ]

        self.width = width
        self.height = height

    @property
    def width(self) -> float:
        c = self._corners
        return float(c[2].x) - float(c[0].x)

    @width.setter
    def width(self, width):
        self.update_width(width)

    def update_width(self, width, factor=0.5):
        rv = width * factor
        top_left, _, bottom_right, _ = self._corners
        handle_pos = self._handle.pos
        connections = self._connections
        for c in self._width_constraints:
            connections.remove_constraint(self, c)

        self._width_constraints = [
            constraint(vertical=(top_left, handle_pos), delta=width - rv),
            constraint(vertical=(handle_pos, bottom_right), delta=rv),
        ]

        for c in self._width_constraints:
            connections.add_constraint(self, c)
        self.request_update()

    @property
    def height(self) -> float:
        c = self._corners
        return float(c[2].y) - float(c[0].y)

    @height.setter
    def height(self, height):
        self.update_height(height)

    def update_height(self, height, factor=0.5):
        rh = height * factor
        top_left, _, bottom_right, _ = self._corners
        handle_pos = self._handle.pos
        connections = self._connections
        for c in self._height_constraints:
            connections.remove_constraint(self, c)

        self._height_constraints = [
            constraint(horizontal=(top_left, handle_pos), delta=height - rh),
            constraint(horizontal=(handle_pos, bottom_right), delta=rh),
        ]

        for c in self._height_constraints:
            connections.add_constraint(self, c)
        self.request_update()

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape) -> None:
        self._shape = shape
        self.request_update()

    def css_nodes(self) -> Iterator[CssNode]:
        return traverse_css_nodes(self._shape) if self._shape else iter(())

    def handles(self):
        return [self._handle]

    def ports(self):
        return self._ports

    def update_shapes(self, event=None):
        """Updating the shape configuration, e.g. when extra elements have to
        be drawn or when styling changes."""

    def update(self, context):
        side = self.connected_side
        if not self.shape or self._last_connected_side != side:
            self._last_connected_side = side
            self.update_shapes()

        return self.shape.size(context, bounding_box=self.dimensions())

    @property
    def connected_side(self) -> str | None:
        cinfo = self._connections.get_connection(self._handle)
        return cinfo.connected.port_side(cinfo.port) if cinfo else None

    def point(self, x, y):
        return distance_rectangle_point(self.dimensions(), (x, y))

    def draw(self, context):
        if self.shape:
            self.shape.draw(context, self.dimensions())

    def dimensions(self):
        top_left, _, bottom_right, _ = self._corners
        return Rectangle(top_left.x, top_left.y, x1=bottom_right.x, y1=bottom_right.y)

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        save_func("point", tuple(map(float, self._handle.pos)))

        if c := self._connections.get_connection(self._handle):
            save_func("connection", c.connected)

        super().save(save_func)

    def load(self, name, value):
        if name == "point":
            self._handle.pos = literal_eval(value)
        elif name == "connection":
            self._load_connection = value
        else:
            super().load(name, value)

    def postload(self):
        super().postload()
        if hasattr(self, "_load_connection"):
            postload_connect(self, self._handle, self._load_connection)
            del self._load_connection

        self.update_shapes()
        self._connections.solve()
