import ast

from gaphas.connector import Handle, LinePort
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.item import Item

from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import Named
from gaphor.diagram.shapes import (
    Box,
    DrawContext,
    EditableText,
    IconBox,
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

        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(text=lambda: stereotypes_str(self.subject, ("proxy",))),
            EditableText(text=lambda: self.subject and self.subject.name or ""),
        )

    def save(self, save_func):
        save_func("matrix", tuple(self.matrix))
        super().save(save_func)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
        else:
            super().load(name, value)

    def dimensions(self):
        return Rectangle(-8, -8, 16, 16)

    def point(self, pos):
        return distance_rectangle_point(self.dimensions(), pos)

    def draw(self, context):
        self.shape.draw(
            DrawContext.from_context(context, self.style), self.dimensions()
        )
