"""Generalization --"""

from __future__ import annotations

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.diagram import Diagram
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import Box
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(
    UML.Generalization,
    head=UML.Generalization.specific,
    tail=UML.Generalization.general,
)
class GeneralizationItem(LinePresentation):
    def __init__(self, diagram: Diagram, id: str | None = None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(text_stereotypes(self)),
        )

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.watch("subject.appliedStereotype.classifier.name")

    def draw_tail(self, context: DrawContext):
        cr = context.cairo
        cr.line_to(15, 0)
        cr.move_to(15, -10)
        cr.line_to(0, 0)
        cr.line_to(15, 10)
        cr.close_path()
