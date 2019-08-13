import ast

import gaphas
from gaphas.geometry import Rectangle, distance_rectangle_point

from gaphor.UML.presentation import Presentation, S
from gaphor.diagram.text import text_point_at_line, TextAlign


class Named:
    """
    Marker for any NamedElement presentations.
    """

    pass


class Classified(Named):
    """
    Marker for Classifier presentations.
    """

    pass


def from_package_str(item):
    """
    Display name space info when it is different, then diagram's or
    parent's namespace.
    """
    subject = item.subject
    canvas = item.canvas

    if not subject or not canvas:
        return False

    namespace = subject.namespace
    parent = canvas.get_parent(item)

    # if there is a parent (i.e. interaction)
    if parent and parent.subject and parent.subject.namespace is not namespace:
        return False

    return (
        f"(from {namespace.name})" if namespace is not canvas.diagram.namespace else ""
    )


# Note: the official documentation is using the terms "Shape" and "Edge" for element and line.


class ElementPresentation(Presentation[S], gaphas.Element):
    """
    Presentation for Gaphas Element (box-like) items.

    To create a shape (boxes, text), assign a shape to `self.shape`.
    If the shape can change, for example because styling needs to change, implement
    the method `update_shapes()` and set self.shape there.
    """

    def __init__(self, id=None, model=None, shape=None):
        super().__init__(id, model)
        self._shape = shape

    def _set_shape(self, shape):
        self._shape = shape
        self.request_update()

    shape = property(lambda s: s._shape, _set_shape)

    def update_shapes(self, event=None):
        """
        Updating the shape configuration, e.g. when extra elements have to
        be drawn or when styling changes.
        """
        pass

    def pre_update(self, context):
        cr = context.cairo
        self.min_width, self.min_height = self.shape.size(cr)

    def draw(self, context):
        self._shape.draw(context, Rectangle(0, 0, self.width, self.height))

    def setup_canvas(self):
        super().setup_canvas()
        # Invoke here, since we do not receive events, unless we're attached to a canvas
        self.update_shapes()

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        for prop in ("width", "height"):
            save_func(prop, getattr(self, prop))
        super().save(save_func)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name in ("width", "height"):
            setattr(self, name, ast.literal_eval(value))
        else:
            super().load(name, value)

    def postload(self):
        super().postload()
        self.update_shapes()


class LinePresentation(Presentation[S], gaphas.Line):
    def __init__(
        self,
        id=None,
        model=None,
        style={},
        shape_head=None,
        shape_middle=None,
        shape_tail=None,
    ):
        super().__init__(id, model)

        self._style = {"dash-style": (), "line-width": 2, **style}

        self.shape_head = shape_head
        self.shape_middle = shape_middle
        self.shape_tail = shape_tail

        self.fuzziness = 2
        self._shape_head_rect = None
        self._shape_middle_rect = None
        self._shape_tail_rect = None

    head = property(lambda self: self._handles[0])
    tail = property(lambda self: self._handles[-1])

    def _set_style(self, style):
        self._style.update(style)

    style = property(
        lambda self: self._style.__getitem__,
        _set_style,
        doc="""A line, contrary to an element, has some styling of it's own.""",
    )

    def post_update(self, context):
        def shape_bounds(shape, align):
            if shape:
                size = shape.size(cr)
                x, y = text_point_at_line(points, size, align)
                return Rectangle(x, y, *size)

        super().post_update(context)
        cr = context.cairo
        points = [h.pos for h in self.handles()]
        self._shape_head_rect = shape_bounds(self.shape_head, TextAlign.LEFT)
        self._shape_middle_rect = shape_bounds(self.shape_middle, TextAlign.CENTER)
        self._shape_tail_rect = shape_bounds(self.shape_tail, TextAlign.RIGHT)

    def point(self, pos):
        """Given a point (x, y) return the distance to the canvas item.
        """
        d0 = super().point(pos)
        ds = [
            distance_rectangle_point(shape, pos)
            for shape in (
                self._shape_head_rect,
                self._shape_middle_rect,
                self._shape_tail_rect,
            )
            if shape
        ]
        return min(d0, *ds) if ds else d0

    def draw(self, context):
        cr = context.cairo
        cr.set_line_width(self.style("line-width"))
        if self.style("dash-style"):
            cr.set_dash(self.style("dash-style"), 0)

        super().draw(context)

        for shape, rect in (
            (self.shape_head, self._shape_head_rect),
            (self.shape_middle, self._shape_middle_rect),
            (self.shape_tail, self._shape_tail_rect),
        ):
            if shape:
                shape.draw(context, rect)

    def save(self, save_func):
        def save_connection(name, handle):
            c = self.canvas.get_connection(handle)
            if c:
                save_func(name, c.connected, reference=True)

        super().save(save_func)
        save_func("matrix", tuple(self.matrix))
        for prop in ("orthogonal", "horizontal"):
            save_func(prop, getattr(self, prop))
        points = [tuple(map(float, h.pos)) for h in self.handles()]
        save_func("points", points)

        save_connection("head-connection", self.head)
        save_connection("tail-connection", self.tail)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name == "points":
            points = ast.literal_eval(value)
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
            self._load_orthogonal = ast.literal_eval(value)
        elif name == "horizontal":
            self.horizontal = ast.literal_eval(value)
        elif name in ("head_connection", "head-connection"):
            self._load_head_connection = value
        elif name in ("tail_connection", "tail-connection"):
            self._load_tail_connection = value
        else:
            super().load(name, value)

    def postload(self):
        def get_sink(handle, item):

            hpos = self.canvas.get_matrix_i2i(self, item).transform_point(*handle.pos)
            port = None
            dist = 10e6
            for p in item.ports():
                pos, d = p.glue(hpos)
                if not port or d < dist:
                    port = p
                    dist = d

            return gaphas.aspect.ConnectionSink(item, port)

        def postload_connect(handle, item):
            connector = gaphas.aspect.Connector(self, handle)
            sink = get_sink(handle, item)
            connector.connect(sink)

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
            postload_connect(self.head, self._load_head_connection)
            del self._load_head_connection

        if hasattr(self, "_load_tail_connection"):
            postload_connect(self.tail, self._load_tail_connection)
            del self._load_tail_connection

        super().postload()
