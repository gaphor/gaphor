"""Use case inclusion relationship."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.UML.shapes import text_stereotypes


@represents(UML.Include, head=UML.Include.addition, tail=UML.Include.includingCase)
class IncludeItem(Named, LinePresentation):
    """Use case inclusion relationship."""

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self, lambda: [self.diagram.gettext("include")]),
                Text(text=lambda: self.subject.name or ""),
            ),
            style={"dash-style": (7.0, 5.0)},
        )

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.watch("subject.appliedStereotype.classifier.name").watch(
            "subject[NamedElement].name"
        )
        self.draw_head = draw_arrow_head
