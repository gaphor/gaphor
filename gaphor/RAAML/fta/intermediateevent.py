"""Intermediate Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_from_package,
    text_name,
)
from gaphor.diagram.shapes import Box, draw_border
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.UML.shapes import text_stereotypes


@represents(raaml.IntermediateEvent)
class IntermediateEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                text_stereotypes(
                    self, lambda: [self.diagram.gettext("Intermediate Event")]
                ),
                text_name(self),
                text_from_package(self),
                style={"padding": (12, 4, 12, 4)},
            ),
            draw=draw_intermediate_event,
        )


def draw_intermediate_event(box, context: DrawContext, bounding_box: Rectangle):
    draw_border(box, context, bounding_box)
