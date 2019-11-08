from __future__ import annotations

from typing import Optional, Tuple

from functools import singledispatch

from gi.repository import Gdk, Gtk
from gaphas import Item

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.presentation import Named, Classified


@singledispatch
def InlineEditor(item: Item, view, pos: Optional[Tuple[int, int]] = None) -> bool:
    """
    Show a small editor popup in the diagram. Makes for
    easy editing without resorting to the Element editor.

    In case of a mouse press event, the mouse position
    (relative to the element) are also provided.
    """
    return False


@InlineEditor.register(Named)
def named_item_inline_editor(item, view, pos=None) -> bool:
    """Text edit support for Named items."""

    @transactional
    def update_text(text):
        item.subject.name = text
        popover.popdown()
        return True

    subject = item.subject
    if not subject:
        return False

    box = view.get_item_bounding_box(view.hovered_item)
    entry = popup_entry(subject.name or "", update_text)
    popover = show_popover(entry, view, box)
    return True


def popup_entry(text, update_text):
    buffer = Gtk.EntryBuffer()
    buffer.set_text(text, -1)
    entry = Gtk.Entry.new_with_buffer(buffer)
    entry.set_activates_default(True)
    entry.connect("activate", lambda entry: update_text(entry.get_buffer().get_text()))
    entry.show()
    return entry


def show_popover(widget, view, box):
    popover = Gtk.Popover.new()
    popover.add(widget)
    popover.set_relative_to(view)
    gdk_rect = Gdk.Rectangle()
    gdk_rect.x = box.x
    gdk_rect.y = box.y
    gdk_rect.width = box.width
    gdk_rect.height = box.height
    popover.set_pointing_to(gdk_rect)
    popover.popup()
    return popover
