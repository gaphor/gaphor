"""Interaction diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.Interaction)
class InteractionItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=150, height=100)

        self.shape = Box(
            CssNode(
                "pentagon",
                None,
                Box(
                    text_stereotypes(self),
                    text_name(self),
                ),
            ),
            draw=draw_interaction,
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_interaction(box, context, bounding_box):
    cr = context.cairo
    cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
    stroke(context, fill=True)
    # draw pentagon
    if not box.sizes:
        box.size(context, bounding_box)
    w, h = box.sizes[0]
    h2 = h / 2.0
    cr.move_to(0, h)
    cr.line_to(w - 4, h)
    cr.line_to(w, h2)
    cr.line_to(w, 0)
    stroke(context, fill=False)
