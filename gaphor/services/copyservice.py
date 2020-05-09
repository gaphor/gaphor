"""
Copy / Paste functionality
"""

from typing import Dict, Set

import gaphas

from gaphor.abc import ActionProvider, Service
from gaphor.core import Transaction, action, event_handler
from gaphor.core.modeling import Element, Presentation
from gaphor.core.modeling.collection import collection
from gaphor.diagram.copypaste import copy, paste
from gaphor.ui.event import DiagramSelectionChanged


class CopyService(Service, ActionProvider):
    """
    Copy/Cut/Paste functionality required a lot of thinking:

    Store a list of DiagramItems that have to be copied in a global
    'copy-buffer'.

    - In order to make copy/paste work, the load/save functions should be
      generalized to allow a subset to be saved/loaded (which is needed
      anyway for exporting/importing stereotype Profiles).
    - How much data should be saved? An example use case is to copy a diagram
      item, remove it (the underlying UML element is removed), and then paste
      the copied item. The diagram should act as if we have placed a copy of
      the removed item on the canvas and make the UML element visible again.
    """

    def __init__(self, event_manager, element_factory, diagrams):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.copy_buffer: object = None

        event_manager.subscribe(self._update)

    def shutdown(self):
        self.copy_buffer = set()
        self.event_manager.unsubscribe(self._update)

    @event_handler(DiagramSelectionChanged)
    def _update(self, event):
        diagram_view = event.diagram_view
        win_action_group = diagram_view.get_action_group("win")
        if win_action_group:
            win_action_group.lookup_action("edit-copy").set_enabled(
                bool(diagram_view.selected_items)
            )

    def copy(self, items):
        if items:
            self.copy_buffer = copy(items)

    def paste(self, diagram):
        """
        Paste items in the copy-buffer to the diagram
        """
        canvas = diagram.canvas

        with Transaction(self.event_manager):
            # Create new id's that have to be used to create the items:
            new_items: Set[Presentation] = paste(
                self.copy_buffer, diagram, self.element_factory.lookup
            )

            # move pasted items a bit, so user can see result of his action :)
            for item in new_items:
                item.matrix.translate(10, 10)

            canvas.update_matrices(new_items)

        return new_items

    def update_paste_state(self, view):
        win_action_group = view.get_action_group("win")
        if win_action_group:
            win_action_group.lookup_action("edit-paste").set_enabled(
                bool(self.copy_buffer)
            )

    @action(
        name="edit-copy", shortcut="<Primary>c",
    )
    def copy_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            items = view.selected_items
            self.copy(items)
        self.update_paste_state(view)

    @action(name="edit-cut", shortcut="<Primary>x")
    def cut_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            items = view.selected_items
            self.copy(items)
            for i in list(items):
                i.unlink()
        self.update_paste_state(view)

    @action(name="edit-paste", shortcut="<Primary>v")
    def paste_action(self):
        view = self.diagrams.get_current_view()
        diagram = self.diagrams.get_current_diagram()
        if not view:
            return

        if not self.copy_buffer:
            return

        new_items = self.paste(diagram)

        view.unselect_all()

        for item in new_items:
            view.select_item(item)

        self.event_manager.handle(DiagramSelectionChanged(view, None, new_items))
