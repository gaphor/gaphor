from gaphas.tool import item_tool as _item_tool
from gi.repository import Gtk

from gaphor.diagram.event import DiagramSelectionChanged


def item_tool(event_manager) -> Gtk.GestureDrag:
    gesture = _item_tool()
    gesture.connect_after("drag-begin", on_drag_begin, event_manager)
    gesture.connect_after("drag-update", on_drag_update)
    gesture.connect_after("drag-end", on_drag_end)
    return gesture


def on_drag_begin(gesture, _start_x, _start_y, event_manager):
    view = gesture.get_widget()
    selection = view.selection
    event_manager.handle(
        DiagramSelectionChanged(view, selection.focused_item, selection.selected_items)
    )


def on_drag_update(gesture, _offset_x, _offset_y):
    view = gesture.get_widget()
    view.model.update()


def on_drag_end(gesture, _offset_x, _offset_y):
    view = gesture.get_widget()
    view.selection.dropzone_item = None
    view.model.update()
