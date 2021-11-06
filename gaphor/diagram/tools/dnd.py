from gi.repository import Gdk, GObject, Gtk

from gaphor.diagram.diagramtoolbox import get_tool_def
from gaphor.diagram.tools.placement import create_item
from gaphor.transaction import Transaction


def drop_target_tool(modeling_language, event_manager) -> Gtk.EventController:
    """GTK4 DropTarget tool."""
    drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY)
    drop_target.connect("drop", on_drop, modeling_language, event_manager)
    return drop_target


def on_drop(target, tool_name, x, y, modeling_language, event_manager):
    view = target.get_widget()
    tool_def = get_tool_def(modeling_language, tool_name)
    with Transaction(event_manager):
        create_item(view, tool_def.item_factory, x, y)

    return True
