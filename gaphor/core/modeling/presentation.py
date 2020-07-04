"""
Base code for presentation elements
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
)

from gaphor.core.modeling import Element
from gaphor.core.modeling.properties import association, attribute, relation_one
from gaphor.core.styling import CompiledStyleSheet

if TYPE_CHECKING:
    from gaphas.canvas import Canvas  # noqa
    from gaphas.connector import Handle  # noqa
    from gaphas.item import Item  # noqa
    from gaphas.view import View  # noqa
    from gaphas.matrix import Matrix  # noqa

S = TypeVar("S", bound=Element)


class ItemWrapper:
    def __init__(self, item: Item, view: Optional[View] = None):
        # I think I need the view here, cause I also need to know the states
        # of other items
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

    def item_style(self, item: Item, view=None) -> Dict[str, object]:
        return self._compiled_style_sheet.match(ItemWrapper(item, view))

    def unlink(self):
        self._watcher.unsubscribe_all()
        super().unlink()


class Presentation(Element, Generic[S]):
    """
    This presentation is used to link the behaviors of `gaphor.core.modeling` and `gaphas.Item`.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        def update(event):
            self.request_update()

        self._watcher = self.watcher(default_handler=update)

        self.watch("subject")

    subject: relation_one[S] = association(
        "subject", Element, upper=1, opposite="presentation"
    )

    @property
    def styleSheet(self) -> Optional[StyleSheet]:
        return next(self.model.select(StyleSheet), None,)  # type: ignore[arg-type]

    @property
    def style(self):
        sheet = self.styleSheet
        return sheet and sheet.item_style(self) or {}

    handles: Callable[[Presentation], List[Handle]]
    request_update: Callable[[Presentation], None]

    canvas: Optional[Canvas]

    matrix: Matrix

    def watch(self, path, handler=None):
        """
        Watch a certain path of elements starting with the DiagramItem.
        The handler is optional and will default to a simple
        self.request_update().

        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent(returns self).
        """
        self._watcher.watch(path, handler)
        return self

    def subscribe_all(self):
        """
        Subscribe all watched paths, as defined through `watch()`.
        """
        self._watcher.subscribe_all()

    def unsubscribe_all(self):
        """
        Unsubscribe all watched paths, as defined through `watch()`.
        """
        self._watcher.unsubscribe_all()

    def unlink(self):
        """
        Remove the item from the canvas and set subject to None.
        """
        if self.canvas:
            self.canvas.remove(self)
        super().unlink()


Element.presentation = association(
    "presentation", Presentation, composite=True, opposite="subject"
)
