from gi.repository import Gdk, Gtk

from gaphor.core.modeling import Diagram
from gaphor.diagram.event import DiagramOpened
from gaphor.diagram.instanteditors import instant_editor


def text_edit_tools(event_manager):
    key_tool = Gtk.EventControllerKey.new()
    click_tool = Gtk.GestureClick.new()

    key_tool.connect("key-pressed", on_key_pressed, event_manager)
    click_tool.connect("released", on_double_click, event_manager)
    return key_tool, click_tool


def on_key_pressed(controller, keyval, keycode, state, event_manager):
    view = controller.get_widget()
    item = view.selection.hovered_item
    if item and keyval == Gdk.KEY_F2:
        return instant_editor(item, view, event_manager)


def on_double_click(gesture, n_press, x, y, event_manager):
    view = gesture.get_widget()
    item = view.selection.hovered_item
    if not item or n_press != 2:
        return

    if isinstance(item.subject, Diagram):
        event_manager.handle(DiagramOpened(item.subject))
    else:
        ix, iy = view.get_matrix_v2i(item).transform_point(x, y)
        return instant_editor(item, view, event_manager, (ix, iy))
