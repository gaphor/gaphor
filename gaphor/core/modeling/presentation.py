"""
Base code for presentation elements
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, List, Optional, TypeVar

from gaphor.core.modeling import Element
from gaphor.core.modeling.properties import association, attribute, relation_one

if TYPE_CHECKING:
    from gaphas.canvas import Canvas  # noqa
    from gaphas.connector import Handle  # noqa
    from gaphas.matrix import Matrix  # noqa

S = TypeVar("S", bound=Element)


def read_style_py():
    """
    Intermediate solution to read styling from an external file
    This allows for testing some styles at least.
    """
    from gaphor.services.properties import get_config_dir
    import os.path
    import ast

    sheet_py = os.path.join(get_config_dir(), "styleSheet.py")
    try:
        with open(sheet_py) as f:
            return ast.literal_eval(f.read())
    except OSError:
        return {}


class StyleSheet(Element):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._style = read_style_py()

    styleSheet: attribute[str] = attribute("styleSheet", str)

    def item_style(self, item):
        return self._style


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
        Subscribe all watched paths, as defined through `watch()`.
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
