"""
ExtensionItem -- Graphical representation of an association.
"""

# TODO: for Extension.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.diagram.abc import Named
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import Box, EditableText, Text
from gaphor.diagram.support import represents


@represents(UML.Extension)
class ExtensionItem(LinePresentation, Named):
    """
    ExtensionItem represents associations.
    An ExtensionItem has two ExtensionEnd items. Each ExtensionEnd item
    represents a Property (with Property.association == my association).
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.shape_middle = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"min-width": 0, "min-height": 0},
            ),
            EditableText(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.line_to(0, 0)
        cr.set_source_rgb(0, 0, 0)
        cr.fill()
        cr.move_to(15, 0)
