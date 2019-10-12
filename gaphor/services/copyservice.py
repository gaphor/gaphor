"""
Copy / Paste functionality
"""

from typing import Dict, Set

import gaphas

from gaphor.UML import Element
from gaphor.UML.collection import collection
from gaphor.core import _, event_handler, action, transactional
from gaphor.abc import Service, ActionProvider
from gaphor.ui.event import DiagramSelectionChange


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
        self.copy_buffer: Set[Element] = set()

        event_manager.subscribe(self._update)

    def shutdown(self):
        self.copy_buffer = set()
        self.event_manager.unsubscribe(self._update)

    @event_handler(DiagramSelectionChange)
    def _update(self, event):
        diagram_view = event.diagram_view
        win_action_group = diagram_view.get_action_group("win")
        if win_action_group is not None:
            win_action_group.lookup_action("edit-copy").set_enabled(
                bool(diagram_view.selected_items)
            )

    def copy(self, items):
        if items:
            self.copy_buffer = set(items)

    def copy_func(self, name, value, reference=False):
        """
        Copy an element, preferably from the list of new items,
        otherwise from the element factory.
        If it does not exist there, do not copy it!
        """

        def load_element():
            item = self._new_items.get(value.id)
            if item:
                self._item.load(name, item)
            else:
                item = self.element_factory.lookup(value.id)
                if item:
                    self._item.load(name, item)

        if reference or isinstance(value, Element):
            load_element()
        elif isinstance(value, collection):
            values = value
            for value in values:
                load_element()
        elif isinstance(value, gaphas.Item):
            load_element()
        else:
            # Plain attribute
            self._item.load(name, str(value))

    @transactional
    def paste(self, diagram):
        """
        Paste items in the copy-buffer to the diagram
        """
        canvas = diagram.canvas
        if not canvas:
            return

        copy_items = [c for c in self.copy_buffer if c.canvas]

        # Mapping original id -> new item
        self._new_items: Dict[str, Element] = {}

        # Create new id's that have to be used to create the items:
        for ci in copy_items:
            self._new_items[ci.id] = diagram.create(type(ci))

        # Copy attributes and references. References should be
        #  1. in the ElementFactory (hence they are model elements)
        #  2. referred to in new_items
        #  3. canvas property is overridden
        for ci in copy_items:
            self._item = self._new_items[ci.id]
            ci.save(self.copy_func)

        # move pasted items a bit, so user can see result of his action :)
        # update items' matrix immediately
        # TODO: if it is new canvas, then let's not move, how to do it?
        for item in list(self._new_items.values()):
            item.matrix.translate(10, 10)
            canvas.update_matrix(item)

        # solve internal constraints of items immediately as item.postload
        # reconnects items and all handles has to be in place
        canvas.solver.solve()
        for item in list(self._new_items.values()):
            item.postload()

    @action(
        name="edit-copy", label=_("Copy"), icon_name="edit-copy", shortcut="<Primary>c"
    )
    def copy_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            items = view.selected_items
            copy_items = []
            for i in items:
                copy_items.append(i)
            self.copy(copy_items)
            win_action_group = view.get_action_group("win")
            if win_action_group is not None:
                win_action_group.lookup_action("edit-paste").set_enabled(
                    bool(self.copy_buffer)
                )

    @action(
        name="edit-paste", label="_Paste", icon_name="edit-paste", shortcut="<Primary>v"
    )
    def paste_action(self):
        view = self.diagrams.get_current_view()
        diagram = self.diagrams.get_current_diagram()
        if not view:
            return

        self.paste(diagram)

        view.unselect_all()

        for item in list(self._new_items.values()):
            view.select_item(item)
