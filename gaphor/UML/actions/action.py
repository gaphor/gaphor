"""Action diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_border, stroke
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Action)
class ActionItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
            style={
                "padding": (4, 12, 4, 12),
                "border-radius": 15,
            },
            draw=draw_border,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


@represents(UML.SendSignalAction)
class SendSignalActionItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
            style={"padding": (4, 24, 4, 12)},
            draw=self.draw_border,
        )

        self.watch("subject[NamedElement].name")
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

        stroke(context)


@represents(UML.AcceptEventAction)
class AcceptEventActionItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
            style={"padding": (4, 12, 4, 24)},
            draw=self.draw_border,
        )

        self.watch("subject[NamedElement].name")
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

        stroke(context)
