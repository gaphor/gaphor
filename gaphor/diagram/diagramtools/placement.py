import logging
from typing import Callable, Optional, Type, TypeVar

from gaphas.aspect.connector import Connector as ConnectorAspect
from gaphas.aspect.connector import ItemConnector
from gaphas.aspect.handlemove import HandleMove
from gaphas.tool.placement import PlacementState
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.core import transactional
from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.connectors import Connector
from gaphor.diagram.event import DiagramItemPlaced
from gaphor.diagram.grouping import Group
from gaphor.diagram.presentation import Presentation

log = logging.getLogger(__name__)

P = TypeVar("P", bound=Presentation, covariant=True)
FactoryType = Callable[[Diagram, Optional[Presentation]], Presentation]
ConfigFuncType = Callable[[P], None]


def placement_tool(
    view: GtkView, factory: FactoryType, event_manager, handle_index: int
):
    gesture = Gtk.GestureDrag.new(view)
    placement_state = PlacementState(factory, handle_index)
    gesture.connect("drag-begin", on_drag_begin, placement_state)
    gesture.connect("drag-update", on_drag_update, placement_state)
    gesture.connect("drag-end", on_drag_end, placement_state, event_manager)
    return gesture


def on_drag_begin(gesture, start_x, start_y, placement_state):
    view = gesture.get_widget()
    item = create_item(view, placement_state.factory, start_x, start_y)

    gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    handle = item.handles()[placement_state.handle_index]
    if handle.movable:
        x, y = view.get_matrix_v2i(item).transform_point(start_x, start_y)
        connect_opposite_handle(view, item, x, y, placement_state.handle_index)
        placement_state.moving = HandleMove(item, handle, view)
        placement_state.moving.start_move((start_x, start_y))

    view.selection.set_dropzone_item(None)


def create_item(view, factory, x, y):
    selection = view.selection
    parent = selection.dropzone_item
    item = factory(view.model.diagram, parent)
    x, y = view.get_matrix_v2i(item).transform_point(x, y)
    item.matrix.translate(x, y)
    selection.unselect_all()
    view.selection.set_focused_item(item)
    return item


def connect_opposite_handle(view, new_item, x, y, handle_index):
    try:
        opposite = new_item.opposite(new_item.handles()[handle_index])
    except (KeyError, AttributeError):
        pass
    else:
        # First make sure all matrices are updated:
        new_item.matrix_i2c.set(*view.model.get_matrix_i2c(new_item))

        handle_move = HandleMove(new_item, opposite, view)
        vpos = (x, y)

        sink = handle_move.glue(vpos)
        if sink:
            handle_move.connect(vpos)


def on_drag_update(gesture, offset_x, offset_y, placement_state):
    if placement_state.moving:
        _, x, y = gesture.get_start_point()
        placement_state.moving.move((x + offset_x, y + offset_y))


def on_drag_end(gesture, offset_x, offset_y, placement_state, event_manager):
    if placement_state.moving:
        _, x, y = gesture.get_start_point()
        placement_state.moving.stop_move((x + offset_x, y + offset_y))
        event_manager.handle(DiagramItemPlaced(placement_state.moving.item))


def new_item_factory(
    item_class: Type[Presentation],
    subject_class: Optional[Type[Element]] = None,
    config_func: Optional[ConfigFuncType] = None,
):
    """``config_func`` may be a function accepting the newly created item."""

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

    item_factory.item_class = item_class  # type: ignore[attr-defined]
    return item_factory


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
            callback = DisconnectHandle(self.item, self.handle, self.connections)
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
