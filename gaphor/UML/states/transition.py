"""State transition implementation."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, draw_arrow_tail
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.Transition, head=UML.Transition.source, tail=UML.Transition.target)
class TransitionItem(Named, LinePresentation[UML.Transition]):
    """Representation of state transition."""

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=CssNode(
                "guard",
                None,
                Text(
                    text=lambda: self.subject
                    and self.subject.guard
                    and self.subject.guard.specification
                    and f"[{self.subject.guard.specification}]"
                    or ""
                ),
            ),
            shape_tail=Box(
                text_stereotypes(self),
                text_name(self),
            ),
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.watch("subject[Transition].guard[Constraint].specification")

        self.draw_tail = draw_arrow_tail
