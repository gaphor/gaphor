"""
ExtensionItem -- Graphical representation of an association.
"""

# TODO: for Extension.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine


class ExtensionItem(NamedLine):
    """
    ExtensionItem represents associations. 
    An ExtensionItem has two ExtensionEnd items. Each ExtensionEnd item
    represents a Property (with Property.association == my association).
    """

    __uml__ = UML.Extension

    def __init__(self, id=None):
        NamedLine.__init__(self, id)
        self.watch("subject<Extension>.ownedEnd")

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.line_to(0, 0)
        cr.set_source_rgb(0, 0, 0)
        cr.fill()
        cr.move_to(15, 0)
