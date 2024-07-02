"""Use case diagram item."""

from gaphor import UML
from gaphor.core.modeling.diagram import StyledItem
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    PresentationStyle,
    text_name,
)
from gaphor.diagram.shapes import Box, draw_ellipse
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.UseCase)
class UseCaseItem(Classified, ElementPresentation):
    """Presentation of gaphor.UML.UseCase."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, height=30)

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Classifier].isAbstract", self.update_shapes)
        self.watch("subject[UseCase].name", self.change_name)

        self.presentation_style = PresentationStyle(
            self.diagram.styleSheet, StyledItem(self).name()
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            text_stereotypes(self),
            text_name(self),
            draw=draw_ellipse,
        )
