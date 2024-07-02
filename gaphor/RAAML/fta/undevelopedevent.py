"""Undeveloped Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox, draw_diamond
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.constants import WIDE_FTA_HEIGHT, WIDE_FTA_WIDTH
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.Undeveloped)
class UndevelopedEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=WIDE_FTA_WIDTH, height=WIDE_FTA_HEIGHT)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_undeveloped_event,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("Undeveloped Event")]),
            text_name(self),
            text_from_package(self),
        )


def draw_undeveloped_event(box, context: DrawContext, bounding_box: Rectangle):
    x1 = 0
    x2 = bounding_box.width
    y1 = 0
    y2 = bounding_box.height
    draw_diamond(context, x1, x2, y1, y2)
