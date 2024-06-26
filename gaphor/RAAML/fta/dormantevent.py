"""Dormant Event item definition."""

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
from gaphor.RAAML.fta.undevelopedevent import draw_undeveloped_event
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.DormantEvent)
class DormantEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=70, height=35)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_dormant_event,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("Dormant Event")]),
            text_name(self),
            text_from_package(self),
        )


def draw_dormant_event(box, context: DrawContext, bounding_box: Rectangle):
    draw_undeveloped_event(box, context, bounding_box)
    x1 = bounding_box.width / 5.0
    x2 = bounding_box.width * 4.0 / 5.0
    y1 = bounding_box.height / 5.0
    y2 = bounding_box.height * 4.0 / 5.0
    draw_diamond(context, x1, x2, y1, y2)
