"""Use case diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, Text, draw_ellipse
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.UML.recipes import stereotypes_str


@represents(UML.UseCase)
class UseCaseItem(Classified, ElementPresentation):
    """Presentation of gaphor.UML.UseCase."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, height=30)

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Classifier].isAbstract", self.update_shapes)

    def update_shapes(self, event=None):
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(
                text=lambda: self.subject.name or "",
                width=lambda: self.width,
                style={
                    "font-weight": FontWeight.BOLD,
                    "font-style": FontStyle.ITALIC
                    if self.subject and self.subject.isAbstract
                    else FontStyle.NORMAL,
                },
            ),
            draw=draw_ellipse,
        )
