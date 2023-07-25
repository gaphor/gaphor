from __future__ import annotations

from gaphas.item import NW

from gaphor.abc import ActionProvider, Service
from gaphor.action import action

from gaphor.i18n import gettext

from gaphor.ui.event import DiagramSelectionChanged
from gaphor.core import action, event_handler
from gaphor.core.modeling import Diagram
from gaphor.diagram.presentation import ElementPresentation

from gaphor.transaction import Transaction

class AlignService(Service, ActionProvider):
    def __init__(self, event_manager, diagrams, tools_menu=None, dump_gv=False):
        self.event_manager = event_manager
        self.diagrams = diagrams
        if tools_menu:
            tools_menu.add_actions(self)
        self.dump_gv = dump_gv

        self.event_manager.subscribe(self._selection_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self._selection_changed)

    @event_handler(DiagramSelectionChanged)
    def _selection_changed(self, event=None, focused_item=None):
        self.event = event
        pass

    @action(
        name="align-left", label=gettext("Align left")
    )
    def align_left(self):
        if current_diagram := self.diagrams.get_current_diagram():
            self._align_elements_left(current_diagram, self.event.selected_items)

    def _align_elements_left(self, diagram: Diagram, selected_items):

        with Transaction(self.event_manager) as tx:
            result = {item for item in selected_items if isinstance(item, ElementPresentation)}
            item = result.pop()

            item.width = 200
            item.height = 200

            item.matrix.translate(-30.0,-30.0)

            diagram.update_now(diagram.get_all_items())