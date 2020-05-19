"""
Action diagram item.
"""

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, EditableText, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.Action)
class ActionItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape = Box(
            Text(text=lambda: stereotypes_str(self.subject),),
            EditableText(text=lambda: self.subject.name or ""),
            style={
                "min-width": 50,
                "min-height": 30,
                "padding": (5, 10, 5, 10),
                "border-radius": 15,
            },
            draw=draw_border,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


@represents(UML.SendSignalAction)
class SendSignalActionItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape = Box(
            Text(text=lambda: stereotypes_str(self.subject),),
            EditableText(text=lambda: self.subject.name or ""),
            style={"min-width": 50, "min-height": 30, "padding": (5, 25, 5, 10)},
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

        cr.stroke()


@represents(UML.AcceptEventAction)
class AcceptEventActionItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape = Box(
            Text(text=lambda: stereotypes_str(self.subject),),
            EditableText(text=lambda: self.subject.name or ""),
            style={"min-width": 50, "min-height": 30, "padding": (5, 10, 5, 25)},
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

        cr.stroke()
