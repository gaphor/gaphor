import gaphor.diagram.align
from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.diagram.event import DiagramSelectionChanged
from gaphor.diagram.presentation import ElementPresentation
from gaphor.event import ActionEnabled
from gaphor.transaction import Transaction


class DiagramAlign(Service, ActionProvider):
    def __init__(self, event_manager, diagrams):
        self.event_manager = event_manager
        self.diagrams = diagrams

        event_manager.subscribe(self._on_selection_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self._on_selection_changed)

    @property
    def alignable_elements(self):
        return (
            {
                item
                for item in view.selection.selected_items
                if isinstance(item, ElementPresentation)
            }
            if (view := self.diagrams.get_current_view())
            else ()
        )

    @action(name="win.diagram-align")
    def align_elements(self, target: str):
        if (view := self.diagrams.get_current_view()) and (
            len(elements := self.alignable_elements) > 1
        ):
            with Transaction(self.event_manager):
                align[target](elements)
                view.model.update(view.model.get_all_items())

    @event_handler(DiagramSelectionChanged)
    def _on_selection_changed(self, event=None):
        self.event_manager.handle(
            ActionEnabled("win.diagram-align", len(self.alignable_elements) > 1)
        )


align = {
    "left": gaphor.diagram.align.align_left,
    "right": gaphor.diagram.align.align_right,
    "vertical-center": gaphor.diagram.align.align_vertical_center,
    "top": gaphor.diagram.align.align_top,
    "bottom": gaphor.diagram.align.align_bottom,
    "horizontal-center": gaphor.diagram.align.align_horizontal_center,
    "max-height": gaphor.diagram.align.resize_max_height,
    "max-width": gaphor.diagram.align.resize_max_width,
    "max-size": gaphor.diagram.align.resize_max_size,
}
