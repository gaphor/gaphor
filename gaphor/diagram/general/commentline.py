"""
CommentLine -- A line that connects a comment to another model element.

"""

from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import LinePresentation


class CommentLineItem(LinePresentation):
    def __init__(self, connections, id=None, model=None):
        super().__init__(connections, id, model, style={"dash-style": (7.0, 5.0)})

    def unlink(self):
        assert self.canvas

        canvas = self.canvas
        c1 = canvas.connections.get_connection(self.head)
        c2 = canvas.connections.get_connection(self.tail)
        if c1 and c2:
            adapter = Connector(c1.connected, self)
            adapter.disconnect(self.head)
        super().unlink()
