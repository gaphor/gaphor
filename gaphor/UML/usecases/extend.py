"""Use case extension relationship."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, EditableText, Text, draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.Extend)
class ExtendItem(LinePresentation, Named):
    """Use case extension relationship."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, style={"dash-style": (7.0, 5.0)})

        self.shape_middle = Box(
            Text(text=lambda: stereotypes_str(self.subject, ("extend",))),
            EditableText(text=lambda: self.subject.name or ""),
        )
        self.watch("subject.appliedStereotype.classifier.name").watch(
            "subject[NamedElement].name"
        )
        self.draw_head = draw_arrow_head
