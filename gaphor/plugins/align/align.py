from __future__ import annotations

from gaphor.abc import ActionProvider, Service
from gaphor.core import action
from gaphor.diagram.presentation import ElementPresentation
from gaphor.i18n import gettext
from gaphor.transaction import Transaction


class AlignService(Service, ActionProvider):
    def __init__(self, event_manager, diagrams, tools_menu=None):
        self.event_manager = event_manager
        self.diagrams = diagrams
        if tools_menu:
            tools_menu.add_actions(self)

    def shutdown(self):
        pass

    @action(name="align-left", label=gettext("Align left"))
    def align_left(self):
        self._modify_elements(align_elements_left)

    @action(name="align-right", label=gettext("Align right"))
    def align_right(self):
        self._modify_elements(align_elements_right)

    @action(name="align-vertical-center", label=gettext("Align vertical center"))
    def align_vertical_center(self):
        self._modify_elements(align_elements_vertical_center)

    @action(name="align-top", label=gettext("Align top"))
    def align_top(self):
        self._modify_elements(align_elements_top)

    @action(name="align-bottom", label=gettext("Align bottom"))
    def align_bottom(self):
        self._modify_elements(align_elements_bottom)

    @action(name="align-horizontal-center", label=gettext("Align horizontal center"))
    def align_horizontal_center(self):
        self._modify_elements(align_elements_horizontal_center)

    @action(name="resize-max-width", label=gettext("Max width"))
    def resize_max_width(self):
        self._modify_elements(resize_elements_max_width)

    @action(name="resize-max-height", label=gettext("Max height"))
    def resize_max_height(self):
        self._modify_elements(resize_elements_max_height)

    @action(name="resize-max-size", label=gettext("Max size"))
    def resize_max_size(self):
        self._modify_elements(resize_elements_max_size)

    def _modify_elements(self, f):
        if current_view := self.diagrams.get_current_view():
            current_diagram = self.diagrams.get_current_diagram()
            selected_items = current_view.selection.selected_items

            if len(selected_items) >= 2:
                elements = {
                    item
                    for item in selected_items
                    if isinstance(item, ElementPresentation)
                }

                with Transaction(self.event_manager):
                    f(elements)
                    current_diagram.update(current_diagram.ownedPresentation)


def align_elements_left(elements: set[ElementPresentation]):
    left_edge = _left_edge(elements)

    for item in elements:
        item.matrix.translate(left_edge - item.matrix.x0, 0)


def align_elements_right(elements: set[ElementPresentation]):
    right_edge = _right_edge(elements)

    for item in elements:
        item.matrix.translate(right_edge - (item.matrix.x0 + item.width), 0)


def align_elements_vertical_center(elements: set[ElementPresentation]):
    left_edge = _left_edge(elements)
    right_edge = _right_edge(elements)
    center_edge = left_edge + (right_edge - left_edge) / 2

    for item in elements:
        item.matrix.translate(center_edge - item.matrix.x0 - item.width / 2, 0)


def align_elements_top(elements: set[ElementPresentation]):
    top_edge = _top_edge(elements)

    for item in elements:
        item.matrix.translate(0, top_edge - item.matrix.y0)


def align_elements_bottom(elements: set[ElementPresentation]):
    bottom_edge = _bottom_edge(elements)

    for item in elements:
        item.matrix.translate(0, bottom_edge - (item.matrix.y0 + item.height))


def align_elements_horizontal_center(elements: set[ElementPresentation]):
    top_edge = _top_edge(elements)
    bottom_edge = _bottom_edge(elements)
    center_edge = top_edge + (bottom_edge - top_edge) / 2

    for item in elements:
        item.matrix.translate(0, center_edge - item.matrix.y0 - item.height / 2)


def resize_elements_max_width(elements: set[ElementPresentation]):
    max_width = _max_width(elements)

    for item in elements:
        item.width = max_width


def resize_elements_max_height(elements: set[ElementPresentation]):
    max_height = _max_height(elements)

    for item in elements:
        item.height = max_height


def resize_elements_max_size(elements: set[ElementPresentation]):
    max_width = _max_width(elements)
    max_height = _max_height(elements)

    for item in elements:
        item.width = max_width
        item.height = max_height


def _left_edge(elements: set[ElementPresentation]):
    return min(item.matrix.x0 for item in elements)


def _right_edge(elements: set[ElementPresentation]):
    return max(item.matrix.x0 + item.width for item in elements)


def _top_edge(elements: set[ElementPresentation]):
    return min(item.matrix.y0 for item in elements)


def _bottom_edge(elements: set[ElementPresentation]):
    return max(item.matrix.y0 + item.height for item in elements)


def _max_width(elements: set[ElementPresentation]):
    return max(item.width for item in elements)


def _max_height(elements: set[ElementPresentation]):
    return max(item.height for item in elements)
