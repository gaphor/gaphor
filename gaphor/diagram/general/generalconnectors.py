"""Connectors for general drawing items (Box, Ellipse) with Line."""

from gaphas.connector import Handle, Port

from gaphor.diagram.connectors import Connector
from gaphor.diagram.general.simpleitem import Box, Diamond, Ellipse, Line


@Connector.register(Box, Line)
@Connector.register(Diamond, Line)
@Connector.register(Ellipse, Line)
class SimpleItemLineConnector:
    def __init__(self, element: Box | Diamond | Ellipse, line: Line) -> None:
        assert element.diagram and element.diagram is line.diagram
        self.element = element
        self.line = line

    def allow(self, _handle: Handle, _port: Port) -> bool:
        return True

    def connect(self, _handle: Handle, _port: Port) -> bool:
        return True

    def disconnect(self, _handle: Handle) -> None:
        pass
