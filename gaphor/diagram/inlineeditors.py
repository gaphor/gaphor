from __future__ import annotations

from functools import singledispatch

from gaphas import Item
from gaphas.geometry import Rectangle
from gi.repository import Gdk, Gtk

from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.transaction import Transaction


@singledispatch
def InlineEditor(
    item: Item, view, event_manager, pos: tuple[int, int] | None = None
) -> bool:
    """Show a small editor popup in the diagram. Makes for easy editing without
    resorting to the Element editor.

    In case of a mouse press event, the mouse position (relative to the
    element) are also provided.
    """
    return False


@InlineEditor.register(Named)
def named_item_inline_editor(item, view, event_manager, pos=None) -> bool:
    """Text edit support for Named items."""

    subject = item.subject
    if not subject:
        return False

    if isinstance(item, LinePresentation):
        box = item.middle_shape_size
        i2v = view.get_matrix_i2v(item)
        x, y = i2v.transform_point(box.x, box.y)
        w, h = i2v.transform_distance(box.width, box.height)
        box = Rectangle(x, y, w, h)
    else:
        box = view.get_item_bounding_box(item)
    name = subject.name or ""
    entry = popup_entry(name)

    def update_text():
        with Transaction(event_manager):
            item.subject.name = entry.get_buffer().get_text()

    show_popover(entry, view, box, update_text)

    return True


def popup_entry(text, update_text=None, done=None):
    buffer = Gtk.EntryBuffer()
    buffer.set_text(text, -1)
    entry = Gtk.Entry.new_with_buffer(buffer)
    entry.show()
    return entry


def show_popover(widget, view, box, commit):
    popover = Gtk.Popover.new()
    if Gtk.get_major_version() == 3:
        popover.add(widget)
        popover.set_relative_to(view)
    else:
        popover.set_child(widget)
    gdk_rect = Gdk.Rectangle()
    gdk_rect.x = box.x
    gdk_rect.y = box.y
    gdk_rect.width = box.width
    gdk_rect.height = box.height
    popover.set_pointing_to(gdk_rect)

    should_commit = True

    def on_closed(popover):
        if should_commit:
            commit()

    popover.connect("closed", on_closed)

    def on_escape(popover, keyval, keycode, state):
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and not state & (
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
        ):
            popover.popdown()
            return True
        elif keyval == Gdk.KEY_Escape:
            nonlocal should_commit
            should_commit = False

    if Gtk.get_major_version() == 3:

        def on_escape3(popover, event):
            return on_escape(popover, event.keyval, 0, event.get_state())

        popover.connect("key-press-event", on_escape3)
        popover.popup()
    else:
        controller = Gtk.EventControllerKey.new()
        popover.add_controller(controller)
        controller.connect("key-pressed", on_escape)
        popover.present()

    return popover
