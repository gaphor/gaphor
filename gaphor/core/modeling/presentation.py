"""
Base code for presentation elements
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
)

from gaphor.core.modeling import Element
from gaphor.core.modeling.properties import association, relation_one

if TYPE_CHECKING:
    from gaphas.canvas import Canvas  # noqa
    from gaphas.connector import Handle  # noqa
    from gaphas.matrix import Matrix  # noqa

S = TypeVar("S", bound=Element)


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
