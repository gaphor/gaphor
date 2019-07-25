"""
State transition implementation.
"""

from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, EditableText, Text, draw_arrow_tail
from gaphor.diagram.support import represents


@represents(UML.Transition)
class TransitionItem(LinePresentation, Named):
    """
    Representation of state transition.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape_tail = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"min-width": 0, "min-height": 0},
            ),
            EditableText(text=lambda: self.subject.name or ""),
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.shape_middle = EditableText(
            text=lambda: self.subject
            and self.subject.guard
            and self.subject.guard.specification
            or ""
        )

        self.watch("subject<Transition>.guard<Constraint>.specification")

        self.draw_tail = draw_arrow_tail
