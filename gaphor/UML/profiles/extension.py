"""
ExtensionItem -- Graphical representation of an association.
"""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.Extension)
class ExtensionItem(Named, LinePresentation):
    """ExtensionItem represents associations.

    An ExtensionItem has two ExtensionEnd items. Each ExtensionEnd item
    represents a Property (with Property.association == my association).
    """

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self),
                text_name(self),
            ),
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.line_to(0, 0)
        cr.fill_preserve()
        cr.move_to(15, 0)
