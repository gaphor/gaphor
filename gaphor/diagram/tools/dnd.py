from gi.repository import Gdk, GObject, Gtk

from gaphor.diagram.diagramtoolbox import get_tool_def
from gaphor.diagram.drop import drop
from gaphor.diagram.tools.placement import create_item
from gaphor.event import Notification
from gaphor.i18n import gettext
from gaphor.transaction import Transaction


def drop_target_tool(modeling_language, event_manager) -> Gtk.EventController:
    """GTK4 DropTarget tool."""
    drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY)
    drop_target.connect("drop", on_drop, modeling_language, event_manager)
    return drop_target


def on_drop(target, source_value, x, y, modeling_language, event_manager):
    view = target.get_widget()
    type, value = source_value.split(":", 1)
    if type == "element":
        element_factory = view.model.model
        element = element_factory.lookup(value)
        x, y = view.matrix.inverse().transform_point(x, y)
        with Transaction(event_manager):
            if item := drop(element, view.model, x, y):
                view.selection.unselect_all()
                view.selection.focused_item = item
                return True
            else:
                event_manager.handle(
                    Notification(gettext("Element can’t be represented on a diagram."))
                )

    if type == "tool":
        tool_def = get_tool_def(modeling_language, value)
        with Transaction(event_manager):
            create_item(view, tool_def.item_factory, x, y)
        return True

    return False
