import ast
from typing import Optional

from gaphas.connector import Handle, LinePort, Position
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.item import Item

from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import Named, postload_connect
from gaphor.diagram.shapes import (
    Box,
    EditableText,
    IconBox,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
)
from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.UML.modelfactory import stereotypes_str


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
class ProxyPortItem(Presentation[sysml.ProxyPort], Item, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        h1 = Handle(connectable=True)
        self._handles.append(h1)

        d = self.dimensions()
        top_left = Position((d.x, d.y))
        top_right = Position((d.x1, d.y))
        bottom_right = Position((d.x1, d.y1))
        bottom_left = Position((d.x, d.y1))
        self._ports.append(LinePort(top_left, top_right))
        self._ports.append(LinePort(top_right, bottom_right))
        self._ports.append(LinePort(bottom_right, bottom_left))
        self._ports.append(LinePort(bottom_left, top_left))

        self._last_connected_side = None
        self.watch("subject[NamedElement].name")

    def update_shapes(self):
        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(text=lambda: stereotypes_str(self.subject, ("proxy",))),
            EditableText(text=lambda: self.subject and self.subject.name or ""),
            style=text_position(self.connected_side()),
        )
        self.request_update()

    def connected_side(self) -> Optional[str]:
        if not self.canvas:
            return None

        cinfo = self.canvas.get_connection(self._handles[0])

        return cinfo.connected.port_side(cinfo.port) if cinfo else None

    def dimensions(self):
        return Rectangle(-8, -8, 16, 16)

    def point(self, pos):
        return distance_rectangle_point(self.dimensions(), pos)

    def setup_canvas(self):
        super().setup_canvas()
        self.subscribe_all()
        # Invoke here, since we do not receive events, unless we're attached to a canvas
        self.update_shapes()

    def teardown_canvas(self):
        self.unsubscribe_all()
        super().teardown_canvas()

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))

        assert self.canvas
        c = self.canvas.get_connection(self.handles()[0])
        if c:
            save_func("connection", c.connected)

        super().save(save_func)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        elif name == "connection":
            self._load_connection = value
        else:
            super().load(name, value)

    def postload(self):
        super().postload()
        if hasattr(self, "_load_connection"):
            postload_connect(self, self.handles()[0], self._load_connection)
            del self._load_connection

        self.update_shapes()

    def pre_update(self, context):
        side = self.connected_side()
        if self._last_connected_side != side:
            self._last_connected_side = side
            self.update_shapes()

        self.shape.size(context)

    def draw(self, context):
        self.shape.draw(context, self.dimensions())
