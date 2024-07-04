"""Unsafe Control Action item definition."""

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


@represents(raaml.UnsafeControlAction)
class UnsafeControlActionItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(
                self, lambda: [self.diagram.gettext("Unsafe Control Action")]
            ),
            draw=draw_unsafe_control_action,
        )


def draw_unsafe_control_action(box, context: DrawContext, bounding_box: Rectangle):
    draw_border(box, context, bounding_box)
