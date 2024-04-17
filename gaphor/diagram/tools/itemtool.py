from gaphas.tool import item_tool as _item_tool
from gi.repository import Gdk, Gtk

from gaphor.diagram.event import DiagramSelectionChanged
from gaphor.transaction import Transaction


class DragState:
    def __init__(self) -> None:
        self.dragging = False


def item_tool(event_manager) -> tuple[Gtk.GestureDrag, Gtk.EventControllerKey]:
    state = DragState()
    gesture = _item_tool()
    gesture.connect_after("drag-begin", on_drag_begin, event_manager, state)
    gesture.connect_after("drag-update", on_drag_update, state)
    gesture.connect_after("drag-end", on_drag_end, state)

    key_ctrl = Gtk.EventControllerKey.new()
    key_ctrl.connect("key-pressed", key_pressed, event_manager, state)
    return gesture, key_ctrl


def key_pressed(ctrl, keyval, keycode, _state, event_manager, state):
    if state.dragging and keyval == Gdk.KEY_Escape:
        Transaction.mark_rollback()


def on_drag_begin(gesture, _start_x, _start_y, event_manager, state):
    state.dragging = True
    view = gesture.get_widget()
    selection = view.selection
    event_manager.handle(
        DiagramSelectionChanged(view, selection.focused_item, selection.selected_items)
    )


def on_drag_update(gesture, _offset_x, _offset_y, state):
    view = gesture.get_widget()
    view.model.update()


def on_drag_end(gesture, _offset_x, _offset_y, state):
    state.dragging = False
    view = gesture.get_widget()
    view.selection.dropzone_item = None
    view.model.update()
