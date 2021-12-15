from typing import Optional

from gaphas.connector import Handle, LinePort, Position
from gaphas.geometry import Rectangle, distance_rectangle_point

from gaphor.core import gettext
from gaphor.core.modeling import Presentation
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


@represents(sysml.ProxyPort)
class ProxyPortItem(Presentation[sysml.ProxyPort], HandlePositionUpdate, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self._connections = diagram.connections

        self._handle = Handle(connectable=True)
        self.watch_handle(self._handle)

        d = self.dimensions()
        top_left = Position(d.x, d.y)
        top_right = Position(d.x1, d.y)
        bottom_right = Position(d.x1, d.y1)
        bottom_left = Position(d.x, d.y1)
        self._ports = [
            LinePort(top_left, top_right),
            LinePort(top_right, bottom_right),
            LinePort(bottom_right, bottom_left),
            LinePort(bottom_left, top_left),
        ]

        self._last_connected_side = None
        self.watch("subject[NamedElement].name")
        self.update_shapes()

    def handles(self):
        return [self._handle]

    def ports(self):
        return self._ports

    def update_shapes(self):
        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(text=lambda: stereotypes_str(self.subject, [gettext("proxy")])),
            Text(text=lambda: self.subject and self.subject.name or ""),
            style=text_position(self.connected_side()),
        )
        self.request_update()

    def connected_side(self) -> Optional[str]:
        cinfo = self._connections.get_connection(self._handle)

        return cinfo.connected.port_side(cinfo.port) if cinfo else None

    def dimensions(self):
        x, y = self._handle.pos
        return Rectangle(x - 8, y - 8, 16, 16)

    def point(self, x, y):
        return distance_rectangle_point(self.dimensions(), (x, y))

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))

        c = self._connections.get_connection(self._handle)
        if c:
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

    def update(self, context):
        side = self.connected_side()
        if self._last_connected_side != side:
            self._last_connected_side = side
            self.update_shapes()

        self.shape.size(context)

    def draw(self, context):
        self.shape.draw(context, self.dimensions())
