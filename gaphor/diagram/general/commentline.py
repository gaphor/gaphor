"""
CommentLine -- A line that connects a comment to another model element.

"""

from gaphor.core.modeling.diagram import StyledItem
from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import LinePresentation, PresentationStyle


class CommentLineItem(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.presentation_style = PresentationStyle(
            self.diagram.styleSheet, StyledItem(self).name()
        )

    def unlink(self):
        c1 = self._connections.get_connection(self.head)
        c2 = self._connections.get_connection(self.tail)
        if c1 and c2:
            adapter = Connector(c1.connected, self)
            adapter.disconnect(self.head)
        super().unlink()
