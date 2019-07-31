"""
Use case diagram item.
"""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.diagram.presentation import ElementPresentation, Classified
from gaphor.diagram.shapes import Box, EditableText, Text
from gaphor.diagram.support import represents


@represents(UML.UseCase)
class UseCaseItem(ElementPresentation, Classified):
    """
    Presentation of gaphor.UML.UseCase.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"min-width": 0, "min-height": 0},
            ),
            EditableText(
                text=lambda: self.subject.name or "", style={"font": "sans bold 10"}
            ),
            style={"min-width": 50, "min-height": 30},
            draw=draw_usecase,
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_usecase(box, context, bounding_box):
    cr = context.cairo

    rx = bounding_box.width / 2.0
    ry = bounding_box.height / 2.0

    cr.move_to(bounding_box.width, ry)
    path_ellipse(cr, rx, ry, bounding_box.width, bounding_box.height)
    cr.stroke()
