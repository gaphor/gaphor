"""Base code for presentation elements."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generic, TypeVar

from gaphas.item import Matrices

from gaphor.core.modeling import Element
from gaphor.core.modeling.event import DiagramItemDeleted
from gaphor.core.modeling.properties import association, relation_many, relation_one

if TYPE_CHECKING:
    from gaphor.core.modeling.diagram import Diagram

S = TypeVar("S", bound=Element)


log = logging.getLogger(__name__)

Transient = False


class Presentation(Matrices, Element, Generic[S]):
    """This presentation is used to link the behaviors of
    `gaphor.core.modeling` and `gaphas.Item`.

    Note that Presentations are not managed by the Element Factory.
    Instead, Presentation objects are owned by Diagram. As a result they
    do not emit ElementCreated and ElementDeleted events. Presentations
    have their own create and delete events: DiagramItemCreated and
    DiagramItemDeleted.
    """

    def __init__(self, diagram: Diagram, id=None):
        if id is Transient:
            super().__init__(id=id)
        else:
            super().__init__(id=id, model=diagram.model)
            self.diagram = diagram

        def update(event):
            if self.diagram:
                self.diagram.request_update(self)

        self._watcher = self.watcher(default_handler=update)
        self.watch("subject")
        self.watch("diagram", self._on_diagram_changed)

    subject: relation_one[S] = association(
        "subject", Element, upper=1, opposite="presentation"
    )

    diagram: relation_one[Diagram]

    parent: relation_one[Presentation]
    children: relation_many[Presentation]

    def request_update(self, matrix=True):
        if self.diagram:
            self.diagram.request_update(self, matrix=matrix)

    def watch(self, path, handler=None):
        """Watch a certain path of elements starting with the DiagramItem. The
        handler is optional and will default to a simple self.request_update().

        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent(returns self).
        """
        self._watcher.watch(path, handler)
        return self

    def unsubscribe_all(self):
        """Unsubscribe all watched paths, as defined through `watch()`."""
        self._watcher.unsubscribe_all()

    def unlink(self):
        """Remove the item from the diagram and set subject to None."""
        diagram = self.diagram
        self._watcher.unsubscribe_all()
        if diagram:
            diagram.connections.remove_connections_to_item(self)
        super().unlink()
        if diagram:
            self.handle(DiagramItemDeleted(diagram, self))

    def _on_diagram_changed(self, event):
        log.debug("Diagram changed. Unlinking %s.", self)
        diagram = event.old_value
        if diagram:
            diagram.connections.remove_connections_to_item(self)
            self.unlink()
            self.handle(DiagramItemDeleted(diagram, self))
        if event.new_value:
            raise ValueError("Can not change diagram for a presentation")


Element.presentation = association(
    "presentation", Presentation, composite=True, opposite="subject"
)
Presentation.parent = association("parent", Presentation, upper=1, opposite="children")
Presentation.children = association(
    "children", Presentation, composite=True, opposite="parent"
)
