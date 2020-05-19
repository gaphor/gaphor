"""
ExtensionItem -- Graphical representation of an association.
"""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, EditableText, Text
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


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
            Text(text=lambda: stereotypes_str(self.subject),),
            EditableText(text=lambda: self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
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
