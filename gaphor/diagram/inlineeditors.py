from __future__ import annotations

from functools import singledispatch
from typing import Optional, Tuple

from gaphas import Item
from gaphas.geometry import Rectangle
from gi.repository import Gdk, Gtk

from gaphor.core import transactional
from gaphor.diagram.presentation import LinePresentation, Named


@singledispatch
def InlineEditor(item: Item, view, pos: Optional[Tuple[int, int]] = None) -> bool:
    """Show a small editor popup in the diagram. Makes for easy editing without
    resorting to the Element editor.

    In case of a mouse press event, the mouse position (relative to the
    element) are also provided.
    """
    return False


@InlineEditor.register(Named)
def named_item_inline_editor(item, view, pos=None) -> bool:
    """Text edit support for Named items."""

    @transactional
    def update_text(text):
        item.subject.name = text
        return True

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
        box = view.get_item_bounding_box(view.selection.hovered_item)
    name = subject.name or ""
    entry = popup_entry(name, update_text)

    def escape():
        subject.name = name

    show_popover(entry, view, box, escape)

    return True


def popup_entry(text, update_text, done=None):
    buffer = Gtk.EntryBuffer()
    buffer.set_text(text, -1)
    entry = Gtk.Entry.new_with_buffer(buffer)
    entry.connect("changed", lambda entry: update_text(entry.get_buffer().get_text()))
    entry.show()
    return entry


def show_popover(widget, view, box, escape=None):
    popover = Gtk.Popover.new()
    popover.add(widget)
    popover.set_relative_to(view)
    gdk_rect = Gdk.Rectangle()
    gdk_rect.x = box.x
    gdk_rect.y = box.y
    gdk_rect.width = box.width
    gdk_rect.height = box.height
    popover.set_pointing_to(gdk_rect)

    def on_escape(popover, event):
        if event.keyval == Gdk.KEY_Return and not event.get_state() & (
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
        ):
            popover.popdown()
            return True
        elif event.keyval == Gdk.KEY_Escape and escape:
            escape()

    popover.connect("key-press-event", on_escape)
    popover.popup()
    return popover
