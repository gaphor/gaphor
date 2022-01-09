"""Copy / Paste functionality."""

from typing import Set

from gi.repository import Gdk, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import Transaction, action
from gaphor.core.modeling import Presentation
from gaphor.diagram.copypaste import copy, paste_full, paste_link
from gaphor.ui.event import DiagramSelectionChanged

copy_buffer: object = None


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

        if Gtk.get_major_version() == 3:
            self.clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
            self._owner_change_id = self.clipboard.connect(
                "owner-change", self.on_clipboard_owner_change
            )
        else:
            # TODO: GTK4 - implement Gdk.Clipboard
            ...

    def shutdown(self):
        if Gtk.get_major_version() == 3:
            self.clipboard.disconnect(self._owner_change_id)

    if Gtk.get_major_version() == 3:

        def on_clipboard_owner_change(self, clipboard, event):
            view = self.diagrams.get_current_view()
            if view and not view.is_focus():
                global copy_buffer
                copy_buffer = set()

    def copy(self, items):
        global copy_buffer
        if items:
            copy_buffer = copy(items)

    def paste_link(self, diagram):
        """Paste items in the copy-buffer to the diagram."""
        with Transaction(self.event_manager):
            # Create new id's that have to be used to create the items:
            new_items: Set[Presentation] = paste_link(
                copy_buffer, diagram, self.element_factory.lookup
            )

            # move pasted items a bit, so user can see result of his action :)
            for item in new_items:
                if item.parent not in new_items:
                    item.matrix.translate(10, 10)

        return new_items

    def paste_full(self, diagram):
        with Transaction(self.event_manager):
            # Create new id's that have to be used to create the items:
            new_items: Set[Presentation] = paste_full(
                copy_buffer, diagram, self.element_factory.lookup
            )

            # move pasted items a bit, so user can see result of his action :)
            for item in new_items:
                if item.parent not in new_items:
                    item.matrix.translate(10, 10)

        return new_items

    @action(
        name="edit-copy",
        shortcut="<Primary>c",
    )
    def copy_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            self.clipboard.set_text("", -1)
            items = view.selection.selected_items
            self.copy(items)

    @action(name="edit-cut", shortcut="<Primary>x")
    def cut_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            self.clipboard.set_text("", -1)
            items = view.selection.selected_items
            self.copy(items)
            with Transaction(self.event_manager):
                for i in list(items):
                    i.unlink()

    @action(name="edit-paste-link", shortcut="<Primary>v")
    def paste_link_action(self):
        self._paste_action(self.paste_link)

    @action(name="edit-paste-full", shortcut="<Primary><Shift>v")
    def paste_full_action(self):
        self._paste_action(self.paste_full)

    def _paste_action(self, paster):
        view = self.diagrams.get_current_view()
        diagram = self.diagrams.get_current_diagram()
        if not (view and view.is_focus()):
            return

        if not copy_buffer:
            return

        new_items = paster(diagram)

        selection = view.selection
        selection.unselect_all()
        selection.select_items(*new_items)

        self.event_manager.handle(DiagramSelectionChanged(view, None, new_items))
