from gi.repository import Gdk, Gtk

from gaphor.diagram.inlineeditors import InlineEditor


def text_edit_tools(view):
    key_tool = Gtk.EventControllerKey.new(view)
    key_tool.connect("key-pressed", on_key_pressed)
    click_tool = Gtk.GestureMultiPress.new(view)
    click_tool.connect("released", on_double_click)
    return key_tool, click_tool


def on_key_pressed(controller, keyval, keycode, state):
    view = controller.get_widget()
    item = view.selection.hovered_item
    if item and keyval == Gdk.KEY_F2:
        return InlineEditor(item, view)


def on_double_click(gesture, n_press, x, y):
    view = gesture.get_widget()
    item = view.selection.hovered_item
    if item and n_press == 2:
        ix, iy = view.get_matrix_v2i(item).transform_point(x, y)
        return InlineEditor(item, view, (ix, iy))
