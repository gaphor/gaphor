"""Containment - A relationship that makes an item an ownedElement of another."""

from gaphor import UML
from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import draw_crossed_circle_head
from gaphor.diagram.support import represents


@represents(UML.Package.ownedElement)
class ContainmentItem(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self.draw_tail = draw_crossed_circle_head

    def unlink(self):
        c1 = self._connections.get_connection(self.head)
        c2 = self._connections.get_connection(self.tail)
        if c1 and c2:
            adapter = Connector(c1.connected, self)
            adapter.disconnect(self.head)
        super().unlink()
