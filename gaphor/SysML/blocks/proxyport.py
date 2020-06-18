import ast

from gaphas.connector import Handle, LinePort
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.item import Item

from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import Named, postload_connect
from gaphor.diagram.shapes import (
    Box,
    DrawContext,
    EditableText,
    IconBox,
    SizeContext,
    Text,
    draw_border,
)
from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.UML.modelfactory import stereotypes_str


@represents(sysml.ProxyPort)
class ProxyPortItem(Presentation[sysml.ProxyPort], Item, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        h1 = Handle(connectable=True)
        self._handles.append(h1)
        # self._ports.append(LinePort(h1.pos, h1.pos))

        self.watch("subject[NamedElement].name")

    def update_shapes(self):
        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(text=lambda: stereotypes_str(self.subject, ("proxy",))),
            EditableText(text=lambda: self.subject and self.subject.name or ""),
        )

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
        if hasattr(self, "_load_connection"):
            postload_connect(self, self.handles()[0], self._load_connection)
            del self._load_connection

        super().postload()

    def pre_update(self, context):
        self.shape.size(SizeContext.from_context(context, self.style))

    def draw(self, context):
        self.shape.draw(
            DrawContext.from_context(context, self.style), self.dimensions()
        )
