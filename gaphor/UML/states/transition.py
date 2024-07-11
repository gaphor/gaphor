"""State transition implementation."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, draw_arrow_tail
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes

# mypy: ignore-errors


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
                Text(  # type: ignore[return-value]
                    text=lambda: self.subject
                    and (
                        (
                            self.subject.trigger
                            and self.subject.trigger.name
                            and f"{self.subject.trigger.name}"
                            or ""
                        )
                        + (
                            self.subject.guard
                            and self.subject.guard.specification
                            and f" [{self.subject.guard.specification}]"
                            or ""
                        )
                        + (
                            self.subject.action
                            and self.subject.action.name
                            and f" /{self.subject.action.name}"
                            or ""
                        )
                    )
                ),
            ),
            shape_tail=Box(
                text_stereotypes(self),
                text_name(self),
            ),
        )
        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.watch("subject[Transition].trigger[Behavior].name")
        self.watch("subject[Transition].guard[Constraint].specification")
        self.watch("subject[Transition].action[Behavior].name")

        self.draw_tail = draw_arrow_tail
