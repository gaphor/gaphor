import gaphas.tool.itemtool as itemtool
from gaphas.connector import Handle
from gaphas.item import Item
from gaphas.tool import item_tool as _item_tool
from gaphas.types import Pos
from gaphas.view import GtkView
from gi.repository import Gtk

from gaphor.diagram.event import DiagramSelectionChanged
from gaphor.diagram.presentation import Framed


def item_tool(event_manager) -> Gtk.GestureDrag:
    gesture = _item_tool(find_item_and_handle_at_point=find_item_and_handle_at_point)
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


def find_item_and_handle_at_point(
    view: GtkView, pos: Pos
) -> tuple[Item, Handle | None] | tuple[None, None]:
    item, handle = itemtool.handle_at_point(view, pos)
    return item or next(
        itemtool.item_at_point(view, pos, exclude=set(view.model.select(Framed))), None
    ), handle
