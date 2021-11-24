from gaphas.view import GtkView
from gi.repository import Gdk, Gtk

from gaphor.core import Transaction
from gaphor.core.modeling import Presentation


def shortcut_tool(view, modeling_language, event_manager):
    if Gtk.get_major_version() == 3:
        ctrl = Gtk.EventControllerKey.new(view)
    else:
        ctrl = Gtk.EventControllerKey.new()
    ctrl.connect("key-pressed", on_delete, event_manager)
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
