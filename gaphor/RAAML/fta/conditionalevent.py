"""Conditional Event item definition."""

from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.basicevent import draw_basic_event
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.ConditionalEvent)
class ConditionalEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=70, height=35)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_basic_event,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("Conditional Event")]),
            text_name(self),
            text_from_package(self),
        )
