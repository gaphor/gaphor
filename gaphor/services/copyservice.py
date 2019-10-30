"""
Copy / Paste functionality
"""

from typing import Dict, Set

import gaphas

from gaphor.UML import Element, Presentation
from gaphor.UML.collection import collection
from gaphor.core import _, event_handler, action, transactional
from gaphor.abc import Service, ActionProvider
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
        self.copy_buffer: Set[gaphas.Item] = set()

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
            self.copy_buffer = set(items)

    @transactional
    def paste(self, diagram):
        """
        Paste items in the copy-buffer to the diagram
        """
        canvas = diagram.canvas
        if not canvas:
            return

        copy_items = [c for c in self.copy_buffer if c.canvas]

        # Create new id's that have to be used to create the items:
        new_items: Dict[str, Presentation] = {
            ci.id: diagram.create(type(ci)) for ci in copy_items
        }

        def copy_func(copy):
            def _copy_func(name, value, reference=False):
                """
                Copy an element, preferably from the list of new items,
                otherwise from the element factory.
                If it does not exist there, do not copy it!
                """

                def load_element():
                    item = new_items.get(value.id)
                    if item:
                        copy.load(name, item)
                    else:
                        item = self.element_factory.lookup(value.id)
                        if item:
                            copy.load(name, item)

                if reference or isinstance(value, Element):
                    setattr(copy, name, value)
                elif isinstance(value, collection):
                    values = value
                    for value in values:
                        setattr(copy, name, value)
                elif isinstance(value, gaphas.Item):
                    load_element()
                else:
                    # Plain attribute
                    copy.load(name, str(value))

            return _copy_func

        # Copy attributes and references. References should be
        #  1. in the ElementFactory (hence they are model elements)
        #  2. referred to in new_items
        #  3. canvas property is overridden
        for ci in copy_items:
            ci.save(copy_func(new_items[ci.id]))
            # new_items[ci.id].subject = ci.subject

        # move pasted items a bit, so user can see result of his action :)
        # update items' matrix immediately
        for item in new_items.values():
            item.matrix.translate(10, 10)
            canvas.update_matrix(item)

        # solve internal constraints of items immediately as item.postload
        # reconnects items and all handles have to be in place
        canvas.solver.solve()
        for item in new_items.values():
            item.postload()

        return new_items

    @action(
        name="edit-copy", label=_("Copy"), icon_name="edit-copy", shortcut="<Primary>c"
    )
    def copy_action(self):
        view = self.diagrams.get_current_view()
        if view.is_focus():
            items = view.selected_items
            self.copy(items)
            win_action_group = view.get_action_group("win")
            if win_action_group:
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

        new_items = self.paste(diagram)

        focused_item = view.focused_item
        view.unselect_all()

        for item in new_items.values():
            view.select_item(item)

        new_focused_item = (
            new_items[focused_item.id] if focused_item else new_items.pop()
        )

        self.event_manager.handle(
            DiagramSelectionChanged(view, new_focused_item, new_items)
        )
