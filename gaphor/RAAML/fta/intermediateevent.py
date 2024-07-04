"""Intermediate Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import Box, draw_border
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.UML.compartments import name_compartment


@represents(raaml.IntermediateEvent)
class IntermediateEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(
                self, lambda: [self.diagram.gettext("Intermediate Event")]
            ),
            draw=draw_intermediate_event,
        )


def draw_intermediate_event(box, context: DrawContext, bounding_box: Rectangle):
    draw_border(box, context, bounding_box)
