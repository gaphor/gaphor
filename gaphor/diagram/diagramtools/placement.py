import logging

from gaphas.aspect.connector import Connector as ConnectorAspect
from gaphas.aspect.connector import ItemConnector
from gaphas.tool.itemtool import item_at_point

from gaphor.core import transactional
from gaphor.diagram.connectors import Connector
from gaphor.diagram.event import DiagramItemPlaced
from gaphor.diagram.grouping import Group
from gaphor.diagram.presentation import Presentation

log = logging.getLogger(__name__)


@ConnectorAspect.register(Presentation)
class DiagramItemConnector(ItemConnector):
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
            callback = DisconnectHandle(self.item, self.handle, self.connections)
            if cinfo and cinfo.connected is sink.item:
                # reconnect only constraint - leave model intact
                log.debug("performing reconnect constraint")
                constraint = sink.port.constraint(item.canvas, item, handle, sink.item)
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
                self.connect_handle(sink, callback=callback)

                # adapter requires both ends to be connected.
                connect(handle, sink.port)
            else:
                # new connection
                adapter = Connector(sink.item, item)
                self.connect_handle(sink, callback=callback)
                adapter.connect(handle, sink.port)
        except Exception:
            log.error("Error during connect", exc_info=True)

    @transactional
    def disconnect(self):
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
            log.debug(f"Not disconnecting {item}.{handle} (disabled)")
        else:
            log.debug(f"Disconnecting {item}.{handle}")
            if cinfo:
                adapter = Connector(cinfo.connected, item)
                adapter.disconnect(handle)


class PlacementTool:
    """PlacementTool is used to place items on the canvas."""

    def __init__(self, view, item_factory, event_manager, handle_index=-1):
        """item_factory is a callable.

        It is used to create a CanvasItem that is displayed on the
        diagram.
        """
        _PlacementTool.__init__(
            self,
            view,
            factory=item_factory,
            handle_tool=ConnectHandleTool(view),
            handle_index=handle_index,
        )
        self.event_manager = event_manager
        self._parent = None

    @classmethod
    def new_item_factory(_class, item_class, subject_class=None, config_func=None):
        """``config_func`` may be a function accepting the newly created
        item."""

        def item_factory(diagram, parent=None):
            if subject_class:
                element_factory = diagram.model
                subject = element_factory.create(subject_class)
            else:
                subject = None

            item = diagram.create(item_class, subject=subject)

            adapter = Group(parent, item)
            if parent and adapter.can_contain():
                canvas = diagram.canvas
                canvas.reparent(item, parent=parent)
                adapter.group()

            if config_func:
                config_func(item)

            return item

        item_factory.item_class = item_class  # type: ignore[attr-defined] # noqa: F821
        return item_factory

    @transactional
    def create_item(self, pos):
        """Create an item directly."""
        return self._create_item(pos)

    def on_button_press(self, event):
        view = self.view
        view.selection.unselect_all()
        if super().on_button_press(event):
            try:
                opposite = self.new_item.opposite(
                    self.new_item.handles()[self._handle_index]
                )
            except (KeyError, AttributeError):
                pass
            else:
                # Connect opposite handle first, using the HandleTool's
                # mechanisms

                # First make sure all matrices are updated:
                self.new_item.matrix_i2c.set(*view.canvas.get_matrix_i2c(self.new_item))

                vpos = event.x, event.y

                item = self.handle_tool.glue(self.new_item, opposite, vpos)
                if item:
                    self.handle_tool.connect(self.new_item, opposite, vpos)
            return True
        return False

    def on_button_release(self, event):
        self.event_manager.handle(DiagramItemPlaced(self.new_item))
        return super().on_button_release(event)

    def on_motion_notify(self, event):
        """Change parent item to dropzone state if it can accept diagram item
        object to be created."""
        if self.grabbed_handle:
            return self.handle_tool.on_motion_notify(event)

        view = self.view
        canvas = view.canvas

        try:
            parent = item_at_point(view, (event.x, event.y))
        except KeyError:
            parent = None

        if parent:
            # create dummy adapter
            adapter = Group(parent, self._factory.item_class())
            if adapter and adapter.can_contain():
                view.selection.set_dropzone_item(parent)
                self._parent = parent
            else:
                view.selection.set_dropzone_item(None)
                self._parent = None
            canvas.request_update(parent, matrix=False)
        else:
            if view.selection.dropzone_item:
                canvas.request_update(view.selection.dropzone_item)
            view.selection.set_dropzone_item(None)

    def _create_item(self, pos):
        """Create diagram item and place it within parent's boundaries."""
        parent = self._parent
        view = self.view
        diagram = view.canvas.diagram
        try:
            item = super()._create_item(pos, diagram=diagram, parent=parent)
        finally:
            self._parent = None
            view.selection.set_dropzone_item(None)
        return item
