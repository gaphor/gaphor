"""
Use case diagram item.
"""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, EditableText, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.UseCase)
class UseCaseItem(ElementPresentation, Classified):
    """
    Presentation of gaphor.UML.UseCase.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.shape = Box(
            Text(text=lambda: stereotypes_str(self.subject),),
            EditableText(
                text=lambda: self.subject.name or "",
                style={"font-weight": FontWeight.BOLD},
            ),
            style={"min-width": 50, "min-height": 30},
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
