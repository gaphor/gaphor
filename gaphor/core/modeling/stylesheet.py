from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional, Sequence

from gaphor.core.modeling import Element
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode

if TYPE_CHECKING:
    from gaphas.item import Item  # noqa
    from gaphas.view import View  # noqa


class ItemWrapper:
    def __init__(self, item: Item, view: Optional[View] = None):
        self.item = item
        self.canvas = item.canvas
        self.view = view

    def local_name(self) -> str:
        return type(self.item).__name__.lower()

    def parent(self) -> Optional[ItemWrapper]:
        parent = self.canvas.get_parent(self.item)
        return ItemWrapper(parent, self.view) if parent else None

    def children(self) -> Iterator[ItemWrapper]:
        children = self.canvas.get_children(self.item)
        view = self.view
        return (ItemWrapper(child, view) for child in children)

    def attribute(self, name: str) -> str:
        return ""

    def state(self) -> Sequence[str]:
        view = self.view
        if view:
            item = self.item
            return (
                "active" if item in view.selected_items else "",
                "focused" if item is view.focused_item else "",
                "hovered" if item is view.hovered_item else "",
                "drop" if item is view.dropzone_item else "",
            )
        return ()


class StyleSheet(Element):
    _compiled_style_sheet: CompiledStyleSheet

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.compile_style_sheet()

    styleSheet: attribute[str] = attribute("styleSheet", str, "")

    def compile_style_sheet(self) -> None:
        self._compiled_style_sheet = CompiledStyleSheet(self.styleSheet)

    def match(self, node: StyleNode) -> Style:
        return self._compiled_style_sheet.match(node)

    def item_style(self, item: Item, view=None) -> Style:
        return self.match(ItemWrapper(item, view))

    def handle(self, event):
        # Ensure compiled style sheet is always up to date:
        if (
            isinstance(event, AttributeUpdated)
            and event.property is StyleSheet.styleSheet
        ):
            self.compile_style_sheet()

        super().handle(event)
