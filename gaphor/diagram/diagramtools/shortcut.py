import functools

from gaphas.view import GtkView
from gi.repository import Gdk, GLib, Gtk

from gaphor.core import Transaction
from gaphor.core.modeling import Presentation


def shortcut_tool(view, modeling_language, event_manager):
    ctrl = Gtk.EventControllerKey.new(view)
    ctrl.connect("key-pressed", on_delete, event_manager)
    ctrl.connect("key-pressed", on_shortcut, modeling_language)
    return ctrl


def on_delete(ctrl, keyval, keycode, state, event_manager):
    """Handle the 'Delete' key.

    This can not be handled directly (through GTK's accelerators),
    otherwise this key will confuse the text edit stuff.
    """
    view: GtkView = ctrl.get_widget()
    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace) and (
        state == 0 or state & Gdk.ModifierType.MOD2_MASK
    ):
        delete_selected_items(view, event_manager)
        return True
    return False


def delete_selected_items(view: GtkView, event_manager):
    with Transaction(event_manager):
        items = view.selection.selected_items
        for i in list(items):
            if isinstance(i, Presentation):
                i.unlink()
            else:
                if i.diagram:
                    i.diagram.remove(i)


def on_shortcut(ctrl, keyval, keycode, state, modeling_language):
    # accelerator keys are lower case. Since we handle them in a key-press event
    # handler, we'll need the upper-case versions as well in case Shift is pressed.
    view: GtkView = ctrl.get_widget()
    for _title, items in modeling_language.toolbox_definition:
        for action_name, _label, _icon_name, shortcut, *rest in items:
            if not shortcut:
                continue
            keys, mod = parse_shortcut(shortcut)
            if state == mod and keyval in keys:
                view.get_toplevel().get_action_group("diagram").lookup_action(
                    "select-tool"
                ).change_state(GLib.Variant.new_string(action_name))
                return True
    return False


_upper_offset = ord("A") - ord("a")


@functools.lru_cache(maxsize=None)
def parse_shortcut(shortcut):
    key, mod = Gtk.accelerator_parse(shortcut)
    return (key, key + _upper_offset), mod
