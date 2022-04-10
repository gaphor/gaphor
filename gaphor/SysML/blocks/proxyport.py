from typing import Generic, Optional

from gaphas.connector import Handle, LinePort, Position
from gaphas.constraint import constraint
from gaphas.geometry import Rectangle, distance_rectangle_point

from gaphor.core import gettext
from gaphor.core.modeling.presentation import Presentation, S
from gaphor.diagram.presentation import HandlePositionUpdate, Named, postload_connect
from gaphor.diagram.shapes import (
    Box,
    IconBox,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
)
from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.UML.recipes import stereotypes_str


def text_position(position):
    return {
        "text-align": TextAlign.LEFT
        if position == "left"
        else (TextAlign.RIGHT if position == "right" else TextAlign.CENTER),
        "vertical-align": VerticalAlign.TOP
        if position == "top"
        else (VerticalAlign.BOTTOM if position == "bottom" else VerticalAlign.MIDDLE),
    }


class AttachedPresentation(Presentation[S], HandlePositionUpdate, Generic[S]):
    """An attached presentation is a base type for all sorts of element-like
    presentations that can be attached to an element.

    E.g. ports, pins and parameter nodes.
    """

    def __init__(self, diagram, id=None, width=16, height=16):
        super().__init__(diagram, id)
        self._connections = diagram.connections
        self._width = width
        self._height = height

        handle = self._handle = Handle(connectable=True)
        self.watch_handle(handle)

        rh = width / 2
        rv = height / 2
        top_left = Position(-rh, -rv)
        top_right = Position(rh, -rv)
        bottom_right = Position(rh, rv)
        bottom_left = Position(-rh, rv)

        add = diagram.connections.add_constraint
        add(self, constraint(horizontal=(top_left, handle.pos), delta=rh))
        add(self, constraint(horizontal=(handle.pos, top_right), delta=-rh))
        add(self, constraint(horizontal=(handle.pos, bottom_right), delta=rh))
        add(self, constraint(horizontal=(bottom_left, handle.pos), delta=-rh))
        add(self, constraint(vertical=(top_left, handle.pos), delta=rv))
        add(self, constraint(vertical=(top_right, handle.pos), delta=-rv))
        add(self, constraint(vertical=(handle.pos, bottom_right), delta=rv))
        add(self, constraint(vertical=(handle.pos, bottom_left), delta=-rv))
        self._ports = [
            LinePort(top_left, top_right),
            LinePort(top_right, bottom_right),
            LinePort(bottom_right, bottom_left),
            LinePort(bottom_left, top_left),
        ]

        self._shape = None
        self._last_connected_side = None

    def _set_shape(self, shape):
        self._shape = shape
        self.request_update()

    shape = property(lambda s: s._shape, _set_shape)

    def handles(self):
        return [self._handle]

    def ports(self):
        return self._ports

    def update_shapes(self, event=None):
        """Updating the shape configuration, e.g. when extra elements have to
        be drawn or when styling changes."""

    def update(self, context):
        side = self.connected_side()
        if not self.shape or self._last_connected_side != side:
            self._last_connected_side = side
            self.update_shapes()

        self.shape.size(context)

    def point(self, x, y):
        return distance_rectangle_point(self.dimensions(), (x, y))

    def draw(self, context):
        self.shape.draw(context, self.dimensions())

    def connected_side(self) -> Optional[str]:
        cinfo = self._connections.get_connection(self._handle)

        return cinfo.connected.port_side(cinfo.port) if cinfo else None

    def dimensions(self):
        w = self._width
        h = self._height
        x, y = self._handle.pos
        return Rectangle(x - w / 2, y - h / 2, w, h)

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))

        if c := self._connections.get_connection(self._handle):
            save_func("connection", c.connected)

        super().save(save_func)

    def load(self, name, value):
        if name == "connection":
            self._load_connection = value
        else:
            super().load(name, value)

    def postload(self):
        super().postload()
        if hasattr(self, "_load_connection"):
            postload_connect(self, self._handle, self._load_connection)
            del self._load_connection

        self.update_shapes()


@represents(sysml.ProxyPort)
class ProxyPortItem(Named, AttachedPresentation[sysml.ProxyPort]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=16, height=16)
        self.watch("subject[NamedElement].name")

    def update_shapes(self):
        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(text=lambda: stereotypes_str(self.subject, [gettext("proxy")])),
            Text(text=lambda: self.subject and self.subject.name or ""),
            style=text_position(self.connected_side()),
        )
