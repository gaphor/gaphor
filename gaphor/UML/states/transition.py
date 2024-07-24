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
                "trigger-guard-action",
                None,
                Text(text=self.trigger_guard_action_text),
            ),
            shape_tail=Box(
                text_stereotypes(self),
                text_name(self),
            ),
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.watch("subject[Transition].trigger.name")
        self.watch("subject[Transition].guard.specification")
        self.watch("subject[Transition].action.name")

        self.draw_tail = draw_arrow_tail

    def trigger_guard_action_text(self) -> str:
        if not self.subject:
            return ""

        trigger_text = self.subject.trigger and self.subject.trigger.name or ""
        guard_text = (
            self.subject.guard
            and self.subject.guard.specification
            and f"[{self.subject.guard.specification}]"
            or ""
        )
        action_text = (
            self.subject.action
            and self.subject.action.name
            and f"/{self.subject.action.name}"
            or ""
        )

        return " ".join(t for t in [trigger_text, guard_text, action_text] if t)
