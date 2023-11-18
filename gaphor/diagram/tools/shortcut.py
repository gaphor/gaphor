from gaphas.view import GtkView
from gi.repository import Gdk, Gtk

from gaphor.core import Transaction
from gaphor.core.modeling import Presentation
from gaphor.diagram.deletable import item_explicitly_deletable
from gaphor.event import Notification
from gaphor.i18n import gettext


def shortcut_tool(view, event_manager):
    ctrl = Gtk.EventControllerKey.new()
    ctrl.connect("key-pressed", on_delete, event_manager)
    return ctrl


def on_delete(ctrl, keyval, keycode, state, event_manager):
    """Handle the 'Delete' key.

    This can not be handled directly (through GTK's accelerators),
    otherwise this key will confuse the text edit stuff.
    """
    view: GtkView = ctrl.get_widget()
    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace):
        delete_selected_items(view, event_manager)
        return True
    return False


def delete_selected_items(view: GtkView, event_manager):
    with Transaction(event_manager):
        items = view.selection.selected_items
        for i in list(items):
            assert isinstance(i, Presentation)
            if item_explicitly_deletable(i):
                i.unlink()
            else:
                event_manager.handle(
                    Notification(gettext("Selected diagram item is not deletable"))
                )
