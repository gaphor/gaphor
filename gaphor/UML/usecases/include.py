"""Use case inclusion relationship."""

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Include)
class IncludeItem(LinePresentation, Named):
    """Use case inclusion relationship."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, style={"dash-style": (7.0, 5.0)})

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.shape_middle = Box(
            Text(text=lambda: stereotypes_str(self.subject, (gettext("include"),))),
            Text(text=lambda: self.subject.name or ""),
        )

        self.watch("subject.appliedStereotype.classifier.name").watch(
            "subject[NamedElement].name"
        )
        self.draw_head = draw_arrow_head
