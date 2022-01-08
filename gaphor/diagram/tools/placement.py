import logging
from typing import Optional

from gaphas.decorators import g_async
from gaphas.handlemove import HandleMove
from gaphas.move import MoveType
from gaphas.view import GtkView
from gi.repository import GLib, Gtk

from gaphor.core.eventmanager import EventManager
from gaphor.diagram.diagramtoolbox import ItemFactory
from gaphor.diagram.event import DiagramItemPlaced
from gaphor.diagram.grouping import Group
from gaphor.diagram.inlineeditors import InlineEditor
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.tools.dropzone import grow_parent

log = logging.getLogger(__name__)


class PlacementState:
    def __init__(
        self, factory: ItemFactory, event_manager: EventManager, handle_index: int
    ):
        self.factory = factory
        self.event_manager = event_manager
        self.handle_index = handle_index
        self.moving: Optional[MoveType] = None


def placement_tool(
    view: GtkView, factory: ItemFactory, event_manager, handle_index: int
):
    gesture = (
        Gtk.GestureDrag.new(view)
        if Gtk.get_major_version() == 3
        else Gtk.GestureDrag.new()
    )
    placement_state = PlacementState(factory, event_manager, handle_index)
    gesture.connect("drag-begin", on_drag_begin, placement_state)
    gesture.connect("drag-update", on_drag_update, placement_state)
    gesture.connect("drag-end", on_drag_end, placement_state)
    return gesture


def on_drag_begin(gesture, start_x, start_y, placement_state):
    view = gesture.get_widget()
    gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    item = create_item(view, placement_state.factory, start_x, start_y)

    handle = item.handles()[placement_state.handle_index]
    if handle.movable:
        connect_opposite_handle(
            view, item, start_x, start_y, placement_state.handle_index
        )
        placement_state.moving = HandleMove(item, handle, view)
        placement_state.moving.start_move((start_x, start_y))
    else:
        placement_state.event_manager.handle(DiagramItemPlaced(item))

    view.selection.dropzone_item = None


def create_item(view, factory, x, y):
    selection = view.selection
    parent = selection.dropzone_item
    item = factory(view.model, parent)
    x, y = view.get_matrix_v2i(item).transform_point(x, y)
    item.matrix.translate(x, y)
    view.model.update_now({item})
    maybe_group(parent, item)
    selection.unselect_all()
    view.selection.focused_item = item
    return item


def maybe_group(parent, item):
    adapter = Group(parent, item)
    if parent and adapter.can_contain():
        grow_parent(parent, item)
        item.change_parent(parent)
        adapter.group()


def connect_opposite_handle(view, new_item, x, y, handle_index):
    try:
        opposite = new_item.opposite(new_item.handles()[handle_index])
    except (KeyError, AttributeError):
        pass
    else:
        if opposite.connectable:
            vpos = (x, y)
            handle_move = HandleMove(new_item, opposite, view)
            sink = handle_move.glue(vpos)
            if sink:
                handle_move.connect(vpos)


def on_drag_update(gesture, offset_x, offset_y, placement_state):
    if placement_state.moving:
        _, x, y = gesture.get_start_point()
        placement_state.moving.move((x + offset_x, y + offset_y))


def on_drag_end(gesture, offset_x, offset_y, placement_state):
    if placement_state.moving:
        view = gesture.get_widget()
        _, x, y = gesture.get_start_point()
        item = placement_state.moving.item
        placement_state.moving.stop_move((x + offset_x, y + offset_y))
        connect_opposite_handle(view, item, x, y, placement_state.handle_index)
        placement_state.event_manager.handle(DiagramItemPlaced(item))
        open_editor(item, view, placement_state.event_manager)


@g_async(priority=GLib.PRIORITY_LOW)
def open_editor(item, view, event_manager):
    if isinstance(item, ElementPresentation):
        InlineEditor(item, view, event_manager)
