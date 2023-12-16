"""Copy / Paste functionality."""

from __future__ import annotations

from typing import Callable, Collection

from gi.repository import Gdk, GLib, GObject

from gaphor.abc import ActionProvider, Service
from gaphor.core import Transaction, action
from gaphor.core.modeling import Diagram, Presentation
from gaphor.diagram.copypaste import Opaque, copy_full, paste_full, paste_link


class CopyBuffer(GObject.Object):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    buffer = GObject.Property(type=object)


class CopyService(Service, ActionProvider):
    """Copy/Cut/Paste functionality required a lot of thinking:

    Store a list of DiagramItems that have to be copied in a global
    'copy-buffer'.

    - In order to make copy/paste work, the load/save functions should be
      generalized to allow a subset to be saved/loaded (which is needed
      anyway for exporting/importing stereotype Profiles).
    - How much data should be saved? An example use case is to copy a diagram
      item, remove it (the underlying UML element is removed), and then paste
      the copied item. The diagram should act as if we have placed a copy of
      the removed item on the diagram and make the UML element visible again.
    """

    def __init__(self, event_manager, element_factory, diagrams):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams

        self.clipboard = Gdk.Display.get_default().get_primary_clipboard()

    def shutdown(self):
        pass

    def copy(self, items: Collection[Presentation]) -> None:
        if items:
            copy_buffer = copy_full(items, self.element_factory.lookup)
            v = GObject.Value(CopyBuffer.__gtype__, CopyBuffer(buffer=copy_buffer))
            self.clipboard.set_content(Gdk.ContentProvider.new_for_value(v))

    def paste_link(
        self,
        diagram: Diagram,
        callback: Callable[[set[Presentation]], None] | None = None,
    ) -> None:
        self._paste(diagram, paste_link, callback)

    def paste_full(
        self,
        diagram: Diagram,
        callback: Callable[[set[Presentation]], None] | None = None,
    ) -> None:
        self._paste(diagram, paste_full, callback)

    def _paste(
        self,
        diagram: Diagram,
        paster: Callable[[Opaque, Diagram], set[Presentation]],
        callback: Callable[[set[Presentation]], None] | None,
    ) -> None:
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

            if callback:
                callback(new_items)

        self.clipboard.read_value_async(
            CopyBuffer.__gtype__,
            io_priority=GLib.PRIORITY_DEFAULT,
            cancellable=None,
            callback=on_paste,
        )

    @action(
        name="edit-copy",
        shortcut="<Primary>c",
    )
    def copy_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            if items := view.selection.selected_items:
                self.copy(items)
            else:
                return

    @action(name="edit-cut", shortcut="<Primary>x")
    def cut_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            items = view.selection.selected_items
            if not items:
                return

            self.copy(items)

            with Transaction(self.event_manager):
                for i in list(items):
                    i.unlink()

    @action(name="edit-paste-link", shortcut="<Primary>v")
    def paste_link_action(self):
        self._paste_action(paste_link)

    @action(name="edit-paste-full", shortcut="<Primary><Shift>v")
    def paste_full_action(self):
        self._paste_action(paste_full)

    def _paste_action(self, paster):
        view = self.diagrams.get_current_view()
        diagram = self.diagrams.get_current_diagram()
        if not (view and view.is_focus()):
            return

        def select_items(new_items):
            selection = view.selection
            selection.unselect_all()
            selection.select_items(*new_items)

        self._paste(diagram, paster, select_items)
