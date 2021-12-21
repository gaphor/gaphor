"""Conditional Event item definition."""

from gaphor.core import gettext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, IconBox, Text
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.basicevent import draw_basic_event
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.ConditionalEvent)
class ConditionalEventItem(ElementPresentation, Classified):
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
                    self.subject, [gettext("Conditional Event")]
                ),
            ),
            Text(
                text=lambda: self.subject.name or "",
                width=lambda: self.width - 4,
                style={
                    "font-weight": FontWeight.BOLD,
                    "font-style": FontStyle.NORMAL,
                },
            ),
            Text(
                text=lambda: from_package_str(self),
                style={"font-size": "x-small"},
            ),
        )
