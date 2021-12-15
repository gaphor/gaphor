"""Use case diagram item."""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight
from gaphor.UML.recipes import stereotypes_str


@represents(UML.UseCase)
class UseCaseItem(ElementPresentation, Classified):
    """Presentation of gaphor.UML.UseCase."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, height=30)
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(
                text=lambda: self.subject.name or "",
                style={"font-weight": FontWeight.BOLD},
            ),
            draw=draw_usecase,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_usecase(box, context, bounding_box):
    cr = context.cairo

    rx = bounding_box.width / 2.0
    ry = bounding_box.height / 2.0

    cr.move_to(bounding_box.width, ry)
    path_ellipse(cr, rx, ry, bounding_box.width, bounding_box.height)
    stroke(context)
