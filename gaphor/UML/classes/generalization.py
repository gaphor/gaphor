"""Generalization --"""

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.diagram import Diagram
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import Box, Text
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Generalization)
class GeneralizationItem(LinePresentation):
    def __init__(self, diagram: Diagram, id: str = None):
        super().__init__(diagram, id, style={"dash-style": ()})

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.shape_middle = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            )
        )
        self.watch("subject.appliedStereotype.classifier.name")

    def draw_tail(self, context: DrawContext):
        cr = context.cairo
        cr.line_to(15, 0)
        cr.move_to(15, -10)
        cr.line_to(0, 0)
        cr.line_to(15, 10)
        cr.close_path()
