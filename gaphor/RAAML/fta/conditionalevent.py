"""Conditional Event item definition."""

from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox, Text
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.basicevent import draw_basic_event
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.ConditionalEvent)
class ConditionalEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=70, height=35)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_basic_event,
            ),
            Text(
                text=lambda: stereotypes_str(
                    self.subject, [self.diagram.gettext("Conditional Event")]
                ),
            ),
            text_name(self),
            Text(
                text=lambda: from_package_str(self),
                style={"font-size": "x-small"},
            ),
        )
