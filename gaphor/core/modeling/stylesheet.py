from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional, Sequence

from gaphor.core.modeling import Element
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet, Style

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
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._watcher = self.watcher()
        self._watcher.watch("styleSheet", self.update_style_sheet)
        self._watcher.subscribe_all()

        self._compiled_style_sheet = CompiledStyleSheet("")

    styleSheet: attribute[str] = attribute("styleSheet", str)

    def postload(self):
        super().postload()
        if self.styleSheet:
            self.compile_style_sheet(self.styleSheet)

    def update_style_sheet(self, event):
        self.compile_style_sheet(event.new_value)

    def compile_style_sheet(self, css: str) -> None:
        self._compiled_style_sheet = CompiledStyleSheet(css)

    def item_style(self, item: Item, view=None) -> Style:
        return self._compiled_style_sheet.match(ItemWrapper(item, view))

    def unlink(self):
        self._watcher.unsubscribe_all()
        super().unlink()
