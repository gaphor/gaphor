from gi.repository import Gdk, Gtk

from gaphor.diagram.inlineeditors import InlineEditor


def text_edit_tools(view, event_manager):
    if Gtk.get_major_version() == 3:
        key_tool = Gtk.EventControllerKey.new(view)
        click_tool = Gtk.GestureMultiPress.new(view)
    else:
        key_tool = Gtk.EventControllerKey.new()
        click_tool = Gtk.GestureClick.new()

    key_tool.connect("key-pressed", on_key_pressed, event_manager)
    click_tool.connect("released", on_double_click, event_manager)
    return key_tool, click_tool


def on_key_pressed(controller, keyval, keycode, state, event_manager):
    view = controller.get_widget()
    item = view.selection.hovered_item
    if item and keyval == Gdk.KEY_F2:
        return InlineEditor(item, view, event_manager)


def on_double_click(gesture, n_press, x, y, event_manager):
    view = gesture.get_widget()
    item = view.selection.hovered_item
    if item and n_press == 2:
        ix, iy = view.get_matrix_v2i(item).transform_point(x, y)
        return InlineEditor(item, view, event_manager, (ix, iy))
