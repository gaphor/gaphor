from gaphor.C4Model import c4model
from gaphor.core import gettext
from gaphor.core.styling import FontWeight, JustifyContent, TextAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, ellipse, stroke
from gaphor.diagram.support import represents


@represents(c4model.C4Database)
class C4DatabaseItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name")
        self.watch("subject[C4Container].technology")
        self.watch("subject[C4Container].description")
        self.watch("subject[C4Container].type")

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                Text(
                    text=lambda: self.subject.technology
                    and f"[{gettext(self.subject.type)}: {self.subject.technology}]"
                    or f"[{gettext(self.subject.type)}]",
                    style={"font-size": "x-small"},
                ),
                Text(
                    text=lambda: self.subject.description or "",
                    width=lambda: self.width - 8,
                    style={"padding": (4, 0, 0, 0)},
                ),
                style={"padding": (4, 4, 4, 4)},
            ),
            style={
                "text-align": TextAlign.LEFT
                if self.diagram and self.children
                else TextAlign.CENTER,
                "justify-content": JustifyContent.END
                if self.diagram and self.children
                else JustifyContent.CENTER,
            },
            draw=draw_database,
        )


def draw_database(box, context, bounding_box):
    cr = context.cairo
    d = 0.38
    x, y, width, height = bounding_box

    x1 = width + x
    y1 = height + y
    ellipse(cr, x, y - height * d / 2, width, height * d)
    cr.move_to(x1, y)
    cr.line_to(x1, y1)
    cr.curve_to(x1, y1, width / 2, y1 + height * d, x, y1)
    cr.line_to(x, y)

    stroke(context)
