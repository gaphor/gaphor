"""Implementation of interface."""


from gaphor import UML
from gaphor.core.styling import Style
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, stroke
from gaphor.diagram.support import represents
from gaphor.UML.classes.interface import Folded, InterfacePort
from gaphor.UML.compartments import text_stereotypes


@represents(
    UML.InterfaceRealization,
    head=UML.InterfaceRealization.contract,
    tail=UML.InterfaceRealization.implementatingClassifier,
)
class InterfaceRealizationItem(Named, LinePresentation):
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
        self._inline_style: Style = {}

    @property
    def on_folded_interface(self):
        connection = self._connections.get_connection(self.head)
        return (
            "true"
            if (
                connection
                and isinstance(connection.port, InterfacePort)
                and connection.connected.folded != Folded.NONE
            )
            else "false"
        )

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        if context.style.get("dash-style"):
            cr.set_dash((), 0)
            cr.line_to(15, -10)
            cr.line_to(15, 10)
            cr.close_path()
            stroke(context, fill=False, dash=False)
            cr.move_to(15, 0)
