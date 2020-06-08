"""
Base code for presentation elements
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, List, Optional, TypeVar

from gaphor.core.modeling import Element
from gaphor.core.modeling.properties import association, attribute, relation_one
from gaphor.core.styling import parse_stylesheet

if TYPE_CHECKING:
    from gaphas.canvas import Canvas  # noqa
    from gaphas.connector import Handle  # noqa
    from gaphas.matrix import Matrix  # noqa

S = TypeVar("S", bound=Element)


class StyleSheet(Element):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._watcher = self.watcher()
        self._watcher.watch("styleSheet", self.update_style_sheet)
        self._watcher.subscribe_all()

        self._style = {}

    styleSheet: attribute[str] = attribute("styleSheet", str)

    def postload(self):
        super().postload()
        if self.styleSheet:
            self.compile_style_sheet(self.styleSheet)

    def update_style_sheet(self, event):
        self.compile_style_sheet(event.new_value)

    def compile_style_sheet(self, css):
        for selector, style in parse_stylesheet(css):
            if selector != "error":
                self._style = style
                return

    def item_style(self, item):
        return self._style

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
