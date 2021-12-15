"""Implementation of interface."""


from gaphor import UML
from gaphor.core.styling import Style
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.UML.classes.interface import Folded, InterfacePort
from gaphor.UML.recipes import stereotypes_str


@represents(UML.InterfaceRealization)
class InterfaceRealizationItem(LinePresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.shape_middle = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
        )
        self.watch("subject[NamedElement].name")
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
            stroke(context, dash=False)
            cr.move_to(15, 0)
