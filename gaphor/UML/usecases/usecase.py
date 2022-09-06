"""Use case diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight
from gaphor.UML.recipes import stereotypes_str


@represents(UML.UseCase)
class UseCaseItem(Classified, ElementPresentation):
    """Presentation of gaphor.UML.UseCase."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, height=30)
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(
                text=lambda: self.subject.name or "",
                width=lambda: self.width - 24,
                style={"font-weight": FontWeight.BOLD},
            ),
            draw=draw_usecase,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_usecase(box, context, bounding_box):
    cr = context.cairo

    w = bounding_box.width
    h = bounding_box.height
    rx = w / 2.0
    ry = h / 2.0

    cr.move_to(0, ry)
    cr.curve_to(0, ry / 2, rx / 2, 0, rx, 0)
    cr.curve_to(rx * 1.5, 0, w, ry / 2, w, ry)
    cr.curve_to(w, ry * 1.5, rx * 1.5, h, rx, h)
    cr.curve_to(rx / 2, h, 0, ry * 1.5, 0, ry)
    cr.close_path()
    stroke(context)
