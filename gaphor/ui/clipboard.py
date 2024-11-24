"""Copy / Paste functionality."""

from __future__ import annotations

from collections.abc import Collection

from gi.repository import Gdk, GLib, GObject

from gaphor.core import Transaction
from gaphor.core.modeling import Presentation
from gaphor.diagram.copypaste import copy_full, paste_full, paste_link


class CopyBuffer(GObject.Object):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    buffer = GObject.Property(type=object)


class Clipboard:
    """Copy/Cut/Paste functionality for diagrams."""

    def __init__(self, event_manager, element_factory, clipboard=None):
        self.event_manager = event_manager
        self.element_factory = element_factory

        self.clipboard = clipboard or Gdk.Display.get_default().get_clipboard()

    def copy(self, view):
        if items := view.selection.selected_items:
            self._copy(items)

    def cut(self, view):
        items = view.selection.selected_items
        if not items:
            return

        self._copy(items)

        with Transaction(self.event_manager):
            for i in list(items):
                i.unlink()

    def paste_link(self, view):
        self._paste(view, paste_link)

    def paste_full(self, view):
        self._paste(view, paste_full)

    def _copy(self, items: Collection[Presentation]) -> None:
        if items:
            copy_buffer = copy_full(items, self.element_factory.lookup)
            v = GObject.Value(CopyBuffer.__gtype__, CopyBuffer(buffer=copy_buffer))
            self.clipboard.set_content(Gdk.ContentProvider.new_for_value(v))

    def _paste(self, view, paster):
        diagram = view.model

        def on_paste(_source_object, result):
            try:
                copy_buffer = self.clipboard.read_value_finish(result)
            except GLib.GError as e:
                if str(e).startswith("g-io-error-quark:"):
                    return
                raise

            with Transaction(self.event_manager):
                # Create new id's that have to be used to create the items:
                new_items = paster(copy_buffer.buffer, diagram)

                # move pasted items a bit, so user can see result of his action :)
                for item in new_items:
                    if item.parent not in new_items:
                        item.matrix.translate(10, 10)

            selection = view.selection
            selection.unselect_all()
            selection.select_items(*new_items)

        self.clipboard.read_value_async(
            CopyBuffer.__gtype__,
            io_priority=GLib.PRIORITY_DEFAULT,
            cancellable=None,
            callback=on_paste,
        )
