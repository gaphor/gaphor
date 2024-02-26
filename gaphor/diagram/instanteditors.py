from __future__ import annotations

from functools import singledispatch

from gaphas import Item
from gaphas.geometry import Rectangle
from gi.repository import Gdk, Gtk

from gaphor.diagram.presentation import LinePresentation, Named, Valued
from gaphor.transaction import Transaction


@singledispatch
def instant_editor(
    item: Item, view, event_manager, pos: tuple[int, int] | None = None
) -> bool:
    """Show a small editor popup in the diagram. Makes for easy editing without
    resorting to the Element editor.

    In case of a mouse press event, the mouse position (relative to the
    element) are also provided.
    """
    return False


@instant_editor.register(Named)
def named_item_editor(item, view, event_manager, pos=None) -> bool:
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


@instant_editor.register(Valued)
def valued_item_editor(item, view, event_manager, pos=None) -> bool:
    """Text edit support for Valued items."""

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
    value = subject.value or ""
    entry = popup_entry(value)

    def update_text():
        with Transaction(event_manager):
            item.subject.value = entry.get_buffer().get_text()

    show_popover(entry, view, box, update_text)

    return True


def popup_entry(text, update_text=None, done=None):
    buffer = Gtk.EntryBuffer()
    buffer.set_text(text, -1)
    return Gtk.Entry.new_with_buffer(buffer)


def show_popover(widget, view, box, commit):
    popover = Gtk.Popover.new()
    popover.set_child(widget)
    popover.set_parent(view)

    gdk_rect = Gdk.Rectangle()
    gdk_rect.x = box.x
    gdk_rect.y = box.y
    gdk_rect.width = box.width
    gdk_rect.height = box.height
    popover.set_pointing_to(gdk_rect)
    popover.set_position(Gtk.PositionType.TOP)

    should_commit = True

    def on_closed(popover):
        if should_commit:
            commit()
        view.grab_focus()
        popover.unparent()

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

    controller = Gtk.EventControllerKey.new()
    popover.add_controller(controller)
    controller.connect("key-pressed", on_escape)

    if isinstance(widget, Gtk.Entry):
        widget.connect("activate", lambda w: popover.popdown())

    if popover.get_root():
        # Test for root window to avoid segfaults in unit test
        popover.set_visible(True)

    return popover
