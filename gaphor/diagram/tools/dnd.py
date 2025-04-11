from gaphas.tool.itemtool import item_at_point
from gi.repository import Gdk, GObject, Gtk

from gaphor.diagram.diagramtoolbox import get_tool_def
from gaphor.diagram.drop import drop
from gaphor.diagram.group import can_group
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
    drop_target.set_preload(True)
    drop_target.connect("motion", on_motion, modeling_language)
    drop_target.connect("drop", on_drop, modeling_language, event_manager)
    return drop_target


def on_motion(
    target: Gtk.DropTarget, x: float, y: float, modeling_language
) -> Gdk.DragAction:
    view = target.get_widget()
    source_value = target.get_value()

    if view.selection.dropzone_item:
        view.model.request_update(view.selection.dropzone_item)

    if not (
        (parent_item := next(item_at_point(view, (x, y)), None)) and parent_item.subject
    ):
        view.selection.dropzone_item = None
        return Gdk.DragAction.COPY

    if (
        isinstance(source_value, ElementDragData)
        and (len(source_value.elements) == 1)
        and can_group(parent_item.subject, source_value.elements[0])
    ):
        view.selection.dropzone_item = parent_item
        view.model.request_update(parent_item)
    elif (
        isinstance(source_value, ToolboxActionDragData)
        and (tool_def := get_tool_def(modeling_language, source_value.action))
        and can_group(parent_item.subject, tool_def.item_factory.subject_class)
    ):
        view.selection.dropzone_item = parent_item
        view.model.request_update(parent_item)
    else:
        view.selection.dropzone_item = None

    return Gdk.DragAction.COPY


def on_drop(target, source_value, x, y, modeling_language, event_manager):
    view = target.get_widget()
    if isinstance(source_value, ElementDragData):
        elements = source_value.elements
        new_parent = view.selection.dropzone_item
        view.selection.dropzone_item = None

        with Transaction(event_manager):
            items = []
            for element in elements:
                if item := _drop(view, element, new_parent, x, y):
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
        return True
    elif isinstance(source_value, ToolboxActionDragData):
        tool_def = get_tool_def(modeling_language, source_value.action)
        with Transaction(event_manager):
            create_item(view, tool_def.item_factory, event_manager, x, y)
        return True

    return False


def _drop(view, item, new_parent, x, y):
    return (
        drop(
            item,
            new_parent,
            *view.get_matrix_v2i(new_parent).transform_point(x, y),
        )
        if new_parent
        else drop(
            item,
            view.model,
            *view.matrix.inverse().transform_point(x, y),
        )
    )
