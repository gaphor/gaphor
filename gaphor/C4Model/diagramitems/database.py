from gaphor.C4Model import c4model
from gaphor.diagram.presentation import ElementPresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, ellipse, stroke
from gaphor.diagram.support import represents


@represents(c4model.C4Database)
class C4DatabaseItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject.name")
        self.watch("subject[C4Container].technology")
        self.watch("subject[C4Container].description")
        self.watch("subject[C4Container].type")
        self.watch("children", self.update_shapes)

    def update_shapes(self, event=None):
        diagram = self.diagram
        self.shape = Box(
            text_name(self),
            CssNode(
                "technology",
                self.subject,
                Text(
                    text=lambda: self.subject.technology
                    and f"[{diagram.gettext(self.subject.type)}: {self.subject.technology}]"
                    or f"[{diagram.gettext(self.subject.type)}]",
                ),
            ),
            *(
                ()
                if self.children
                else (
                    CssNode(
                        "description",
                        self.subject,
                        Text(text=lambda: self.subject.description or ""),
                    ),
                )
            ),
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

    stroke(context, fill=True)
