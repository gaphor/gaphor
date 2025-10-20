from gi.repository import Gdk, Gtk

from gaphor.transaction import Transaction


def item_move_tool(event_manager) -> Gtk.EventControllerKey:
    ctrl = Gtk.EventControllerKey.new()
    ctrl.connect("key-pressed", on_key_pressed, event_manager)
    return ctrl


def on_key_pressed(controller, keyval: int, _keycode, _state, event_manager) -> bool:
    view = controller.get_widget()
    items = view.selection.selected_items

    if not items:
        return False

    # NB. Styling uses multiples of 4
    if keyval in (Gdk.KEY_Up, Gdk.KEY_KP_Up):
        dx, dy = (0, -12)
    elif keyval in (Gdk.KEY_Down, Gdk.KEY_KP_Down):
        dx, dy = (0, 12)
    elif keyval in (Gdk.KEY_Left, Gdk.KEY_KP_Left):
        dx, dy = (-12, 0)
    elif keyval in (Gdk.KEY_Right, Gdk.KEY_KP_Right):
        dx, dy = (12, 0)
    else:
        return False

    with Transaction(event_manager):
        for item in items:
            item.matrix.translate(dx, dy)

    return True
