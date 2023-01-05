from gaphas.tool import item_tool as _item_tool
from gaphas.view import GtkView
from gi.repository import Gtk


def item_tool(view: GtkView) -> Gtk.GestureDrag:
    gesture = _item_tool(view)
    gesture.connect_after("drag-end", on_drag_end)
    return gesture


def on_drag_end(gesture, _offset_x, _offset_y):
    view = gesture.get_widget()
    view.selection.dropzone_item = None
