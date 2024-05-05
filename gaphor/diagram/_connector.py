"""Gaphas connectors.

This module ties connectors in Gaphas -- on presentation -- to model
level connectors (gaphor.connectors).
"""

import logging

from gaphas.connector import Connector as ConnectorAspect
from gaphas.connector import ItemConnector, LineConnector

from gaphor.core.modeling import Presentation
from gaphor.diagram.connectors import (
    Connector,
    ItemConnected,
    ItemDisconnected,
    ItemReconnected,
)
from gaphor.diagram.presentation import ElementPresentation, LinePresentation

log = logging.getLogger(__name__)


@ConnectorAspect.register(Presentation)
@ConnectorAspect.register(ElementPresentation)
class PresentationConnector(ItemConnector):
    """Handle Tool (acts on item handles) that uses the Connector protocol to
    connect items to one-another.

    It also adds handles to lines when a line is grabbed in the middle
    of a line segment (points are drawn by the LineSegmentPainter).
    """

    def allow(self, sink):
        adapter = Connector(sink.item, self.item)
        return adapter and adapter.allow(self.handle, sink.port)

    def connect(self, sink):
        """Create connection at handle level and at model level."""
        handle = self.handle
        item = self.item
        cinfo = self.connections.get_connection(handle)

        if cinfo and cinfo.connected is sink.item:
            self.reconnect_handle(sink)
            return

        adapter = Connector(sink.item, item)
        if cinfo:
            self.disconnect()

        self.glue(sink)
        if not sink.port:
            log.warning("No port found", item, sink.item)
            return

        self.connect_handle(sink)
        adapter.connect(handle, sink.port)

    def connect_handle(self, sink):
        super().connect_handle(sink, callback=DisconnectHandle())
        item = self.item
        item.handle(ItemConnected(item, self.handle, sink.item, sink.port))

    def disconnect(self):
        # Model level disconnect and event is handled in callback
        super().disconnect()

    def disconnect_handle(self):
        if cinfo := self.connections.get_connection(self.handle):
            # prevent model level disconnect from triggering
            cinfo.callback.disable = True
        super().disconnect()

    def reconnect_handle(self, sink):
        """Reconnect only constraint - leave model intact."""
        handle = self.handle
        item = self.item
        log.debug("performing reconnect constraint")
        self.glue(sink)
        constraint = sink.constraint(item, handle)
        self.connections.reconnect_item(item, handle, sink.port, constraint=constraint)
        item.handle(ItemReconnected(item, handle, sink.item, sink.port))


@ConnectorAspect.register(LinePresentation)
class LinePresentationConnector(PresentationConnector, LineConnector):
    pass


class DisconnectHandle:
    """Callback for items disconnection using the adapters.

    This is an object so disconnection data can be serialized/deserialized
    using pickle.

    Args:
      item (Item): Connecting item.
      handle (Handle): Handle of connecting item.
      connections (Connections): Connections object containing connection constraints.
    """

    def __init__(self):
        self.disable = False

    def __call__(self, item, handle, connected, port):
        if self.disable:
            log.debug(f"Disconnect callback disabled for {item}.{handle} (disabled)")
        else:
            log.debug(f"Disconnect callback {item}.{handle}")
            adapter = Connector(connected, item)
            adapter.disconnect(handle)
        item.handle(ItemDisconnected(item, handle, connected, port))
