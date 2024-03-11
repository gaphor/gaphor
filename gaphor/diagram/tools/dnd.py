from gi.repository import Gdk, GObject, Gtk

from gaphor.diagram.diagramtoolbox import get_tool_def
from gaphor.diagram.drop import drop
from gaphor.diagram.tools.placement import create_item
from gaphor.event import Notification
from gaphor.i18n import gettext
from gaphor.transaction import Transaction


class ElementDragData(GObject.Object):
    elements = GObject.Property(type=object)


class ToolboxActionDragData(GObject.Object):
    action = GObject.Property(type=str)


def drop_target_tool(modeling_language, event_manager) -> Gtk.EventController:
    """DropTarget tool."""
    drop_target = Gtk.DropTarget.new(GObject.TYPE_NONE, Gdk.DragAction.COPY)
    drop_target.set_gtypes([ElementDragData.__gtype__, ToolboxActionDragData.__gtype__])
    drop_target.connect("drop", on_drop, modeling_language, event_manager)
    return drop_target


def on_drop(target, source_value, x, y, modeling_language, event_manager):
    view = target.get_widget()
    if isinstance(source_value, ElementDragData):
        elements = source_value.elements
        x, y = view.matrix.inverse().transform_point(x, y)
        with Transaction(event_manager):
            items = []
            for element in elements:
                if item := drop(element, view.model, x, y):
                    x += 20
                    y += 20
                    items.append(item)

            if len(items) > 1:
                view.selection.unselect_all()
                view.selection.select_items(*items)
                return True
            if items:
                view.selection.unselect_all()
                view.selection.focused_item = item
                return True
            else:
                event_manager.handle(
                    Notification(gettext("Element can’t be represented on a diagram."))
                )
        return
    elif isinstance(source_value, ToolboxActionDragData):
        tool_def = get_tool_def(modeling_language, source_value.action)
        with Transaction(event_manager):
            create_item(view, tool_def.item_factory, event_manager, x, y)
        return True

    return False
