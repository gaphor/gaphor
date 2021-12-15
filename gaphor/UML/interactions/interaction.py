"""Interaction diagram item."""

from gaphor import UML
from gaphor.core.styling import TextAlign, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Interaction)
class InteractionItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=150, height=100)

        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject),
                    style={
                        "text-align": TextAlign.LEFT,
                    },
                ),
                Text(
                    text=lambda: self.subject.name or "",
                    style={"text-align": TextAlign.LEFT},
                ),
                style={"padding": (4, 4, 4, 4)},
            ),
            style={
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_interaction,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_interaction(box, context, bounding_box):
    cr = context.cairo
    cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
    stroke(context)
    # draw pentagon
    w, h = box.sizes[0]
    h2 = h / 2.0
    cr.move_to(0, h)
    cr.line_to(w - 4, h)
    cr.line_to(w, h2)
    cr.line_to(w, 0)
    stroke(context, fill=False)
