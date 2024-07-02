"""Action diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named, Valued, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.umlfmt import format_call_behavior_action_name


@represents(UML.Action)
class ActionItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.width = 100
        self.shape = Box(
            text_stereotypes(self),
            text_name(self),
            draw=draw_border,
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")


@represents(UML.ValueSpecificationAction)
class ValueSpecificationActionItem(Valued, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.width = 100
        self.shape = Box(
            text_stereotypes(self, lambda: ["valueSpecification"]),
            CssNode("value", None, Text(text=lambda: self.subject.value or "")),
            draw=draw_border,
        )

        self.watch("subject[ValueSpecificationAction].value")


@represents(UML.CallBehaviorAction)
class CallBehaviorActionItem(ActionItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.shape = Box(
            text_stereotypes(self),
            CssNode(
                "name",
                None,
                Text(text=lambda: format_call_behavior_action_name(self.subject)),
            ),
            draw=self.draw_border_with_fork,
        )

        self.watch("subject[CallBehaviorAction].behavior.name")

    def draw_border_with_fork(self, box, context, bounding_box):
        draw_border(box, context, bounding_box)

        cr = context.cairo
        x, y, width, height = bounding_box

        x_offset = width - 15
        y_offset = height - 15
        half_width = 5
        half_height = 5

        cr.move_to(x_offset, y_offset - half_height)
        cr.line_to(x_offset, y_offset + half_height)
        cr.close_path()

        cr.move_to(x_offset - half_width, y_offset)
        cr.line_to(x_offset + half_width, y_offset)
        cr.close_path()

        cr.move_to(x_offset - half_width, y_offset)
        cr.line_to(x_offset - half_width, y_offset + half_height)
        cr.close_path()

        cr.move_to(x_offset + half_width, y_offset)
        cr.line_to(x_offset + half_width, y_offset + half_height)
        cr.close_path()

        stroke(context, fill=True)


@represents(UML.SendSignalAction)
class SendSignalActionItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.shape = Box(
            text_stereotypes(self),
            text_name(self),
            draw=self.draw_border,
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

    def draw_border(self, box, context, bounding_box):
        cr = context.cairo
        d = 15
        x, y, width, height = bounding_box
        cr.move_to(0, 0)
        cr.line_to(width - d, 0)
        cr.line_to(width, height / 2)
        cr.line_to(width - d, height)
        cr.line_to(0, height)
        cr.close_path()

        stroke(context, fill=True)


@represents(UML.AcceptEventAction)
class AcceptEventActionItem(Named, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.shape = Box(
            text_stereotypes(self),
            text_name(self),
            draw=self.draw_border,
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

    def draw_border(self, box, context, bounding_box):
        cr = context.cairo
        d = 15
        x, y, width, height = bounding_box
        cr.move_to(0, 0)
        cr.line_to(width, 0)
        cr.line_to(width, height)
        cr.line_to(0, height)
        cr.line_to(d, height / 2)
        cr.close_path()

        stroke(context, fill=True)
