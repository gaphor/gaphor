"""
CommentLine -- A line that connects a comment to another model element.

"""

from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import LinePresentation


class CommentLineItem(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, style={"dash-style": (7.0, 5.0)})

    def unlink(self):
        c1 = self._connections.get_connection(self.head)
        c2 = self._connections.get_connection(self.tail)
        if c1 and c2:
            adapter = Connector(c1.connected, self)
            adapter.disconnect(self.head)
        super().unlink()
