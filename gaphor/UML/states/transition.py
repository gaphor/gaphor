"""State transition implementation."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_arrow_tail
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Transition)
class TransitionItem(LinePresentation[UML.Transition], Named):
    """Representation of state transition."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.shape_tail = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.shape_middle = Text(
            text=lambda: self.subject
            and self.subject.guard
            and self.subject.guard.specification
            and f"[{self.subject.guard.specification}]"
            or ""
        )

        self.watch("subject[Transition].guard[Constraint].specification")

        self.draw_tail = draw_arrow_tail
