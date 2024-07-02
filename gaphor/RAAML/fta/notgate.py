"""NOT gate item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox, stroke
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR, DEFAULT_FTA_MINOR
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.NOT)
class NOTItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MINOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_not_gate,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("NOT Gate")]),
            text_name(self),
            text_from_package(self),
        )


def draw_not_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    x1 = 0
    x2 = bounding_box.width
    height = bounding_box.height
    cr.move_to(x1, height)
    cr.line_to(x2, 0)
    cr.line_to(x1, 0)
    cr.line_to(x2, height)
    cr.line_to(x1, height)
    stroke(context, fill=True)
