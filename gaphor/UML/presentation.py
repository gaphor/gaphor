"""
Base code for presentation elements
"""

from typing import Generic, Optional, TypeVar, TYPE_CHECKING
from gaphor.UML.properties import umlproperty, association
from gaphor.UML.element import Element

if TYPE_CHECKING:
    from gaphas.canvas import Canvas

S = TypeVar("S", bound=Element)


class Presentation(Element, Generic[S]):
    """
    This presentation is used to link the behaviors of `gaphor.UML.Element` and `gaphas.Item`.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        def update(event):
            self.request_update()

        self._watcher = self.watcher(default_handler=update)

        self.watch("subject")

    subject: umlproperty[S, S] = association(
        "subject", Element, upper=1, opposite="presentation"
    )

    canvas: Optional["Canvas"]

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
