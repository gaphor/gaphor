import logging

from gaphas.aspect.connector import ConnectionSink
from gaphas.aspect.connector import Connector as ConnectorAspect
from gaphas.aspect.connector import ItemConnector

from gaphor.core import transactional
from gaphor.core.modeling.event import RevertibeEvent
from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import Presentation

log = logging.getLogger(__name__)


@ConnectorAspect.register(Presentation)
class PresentationConnector(ItemConnector):
    """Handle Tool (acts on item handles) that uses the Connector protocol to
    connect items to one-another.

    It also adds handles to lines when a line is grabbed on the middle
    of a line segment (points are drawn by the LineSegmentPainter).
    """

    def allow(self, sink):
        adapter = Connector(sink.item, self.item)
        return adapter and adapter.allow(self.handle, sink.port)

    @transactional
    def connect(self, sink):
        """Create connection at handle level and at model level."""
        handle = self.handle
        item = self.item
        cinfo = self.connections.get_connection(handle)

        try:
            if cinfo and cinfo.connected is sink.item:
                # reconnect only constraint - leave model intact
                log.debug("performing reconnect constraint")
                constraint = sink.port.constraint(item, handle, sink.item)
                self.connections.reconnect_item(
                    item, handle, sink.port, constraint=constraint
                )
            elif cinfo:
                # first disconnect but disable disconnection handle as
                # reconnection is going to happen
                adapter = Connector(sink.item, item)
                try:
                    connect = adapter.reconnect
                except AttributeError:
                    connect = adapter.connect
                else:
                    cinfo.callback.disable = True
                self.disconnect()

                # new connection
                self.connect_handle(sink)

                # adapter requires both ends to be connected.
                connect(handle, sink.port)
                item.handle(ItemConnected(item, handle, sink.item, sink.port))
            else:
                # new connection
                adapter = Connector(sink.item, item)
                self.connect_handle(sink)
                adapter.connect(handle, sink.port)
                item.handle(ItemConnected(item, handle, sink.item, sink.port))
        except Exception:
            log.error("Error during connect", exc_info=True)

    def connect_handle(self, sink):
        callback = DisconnectHandle(self.item, self.handle, self.connections)
        super().connect_handle(sink, callback=callback)

    @transactional
    def disconnect(self):
        # Model level disconnect and event is handled in callback
        super().disconnect()


class DisconnectHandle:
    """Callback for items disconnection using the adapters.

    This is an object so disconnection data can be serialized/deserialized
    using pickle.

    :Variables:
     item
        Connecting item.
     handle
        Handle of connecting item.
     disable
        If set, then disconnection is disabled.
    """

    def __init__(self, item, handle, connections):
        self.item = item
        self.handle = handle
        self.connections = connections
        self.disable = False

    def __call__(self):
        handle = self.handle
        item = self.item
        connections = self.connections
        cinfo = connections.get_connection(handle)

        if self.disable:
            log.debug(f"Disconnect callback disabled for {item}.{handle} (disabled)")
        else:
            log.debug(f"Disconnect callback {item}.{handle}")
            if cinfo:
                adapter = Connector(cinfo.connected, item)
                adapter.disconnect(handle)
        self.item.handle(
            ItemDisconnected(self.item, self.handle, cinfo.connected, cinfo.port)
        )


class ItemConnected(RevertibeEvent):
    def __init__(self, element, handle, connected, port):
        self.element = element
        self.handle_index = element.handles().index(handle)
        self.connected = connected
        self.port_index = connected.ports().index(port)

    def revert(self, target):
        # Reverse only the diagram level connection.
        # Associations have their own handlers
        connections = target.diagram.connections
        handle = target.handles()[self.handle_index]
        connector = ConnectorAspect(target, handle, connections)
        cinfo = connections.get_connection(handle)
        if cinfo:
            cinfo.callback.disable = True
        connector.disconnect()


class ItemDisconnected(RevertibeEvent):
    def __init__(self, element, handle, connected, port):
        self.element = element
        self.handle_index = element.handles().index(handle)
        self.connected = connected
        self.port_index = connected.ports().index(port)

    def revert(self, target):
        # Reverse only the diagram level connection.
        # Associations have their own handlers
        connections = target.diagram.connections
        assert connections

        connected = target.diagram.lookup(self.connected.id)
        sink = ConnectionSink(connected, connected.ports()[self.port_index])

        handle = target.handles()[self.handle_index]
        connector = ConnectorAspect(target, handle, connections)
        connector.connect_handle(sink)
        target.handle(ItemConnected(target, handle, sink.item, sink.port))
