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
        self._align_elements(self._align_elements_left)

    @action(
        name="align-right", label=gettext("Align right")
    )
    def align_right(self):
        self._align_elements(self._align_elements_right)

    def _align_elements(self, f):
        if current_diagram := self.diagrams.get_current_diagram():
            elements = {item for item in self.event.selected_items if isinstance(item, ElementPresentation)}
            with Transaction(self.event_manager):
                f(elements)
                current_diagram.update_now(current_diagram.get_all_items())

    def _align_elements_left(self, elements: set[ElementPresentation]):
            left_edge = min(set(map(lambda item : self._pos_x(item), elements)))
            for item in elements:
                item.matrix.translate(left_edge - self._pos_x(item), 0)
            
    def _align_elements_right(self, elements: set[ElementPresentation]):
            right_edge = max(set(map(lambda item : self._pos_x(item) + item.width, elements)))
            for item in elements:
                item.matrix.translate(right_edge - (self._pos_x(item) + item.width), 0)

    def _pos_x(self, item: ElementPresentation):
        _,_,_,_,x,_ = item.matrix.tuple()
        return x

    def _pos_y(self, item: ElementPresentation):
        _,_,_,_,_,y = item.matrix.tuple()
        return y