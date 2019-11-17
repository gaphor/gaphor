"""
Generalization --
"""


from gaphor import UML
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import Box, Text
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.Generalization)
class GeneralizationItem(LinePresentation):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape_middle = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"min-width": 0, "min-height": 0},
            )
        )
        self.watch("subject.appliedStereotype.classifier.name")

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.close_path()
        cr.stroke()
        cr.move_to(15, 0)
