"""Base code for presentation elements."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generic, TypeVar

from gaphas.item import Matrices

from gaphor.core.modeling import Element
from gaphor.core.modeling.event import DiagramItemDeleted, RevertibeEvent
from gaphor.core.modeling.properties import association, relation_many, relation_one

if TYPE_CHECKING:
    from gaphor.core.modeling.diagram import Diagram

S = TypeVar("S", bound=Element)


log = logging.getLogger(__name__)


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
        super().__init__(id=id, model=diagram.model)
        self.diagram = diagram

        def update(event):
            if self.diagram:
                self.diagram.request_update(self)

        self._watcher = self.watcher(default_handler=update)
        self.watch("subject")
        self.watch("children")
        self.watch("diagram", self._on_diagram_changed)
        self.watch("parent", self._on_parent_changed)
        self.matrix.add_handler(self._on_matrix_changed)

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

    def postload(self):
        super().postload()
        if self.parent:
            self.parent.matrix_i2c.add_handler(self._on_matrix_changed)

    def unlink(self):
        """Remove the item from the diagram and set subject to None."""
        self._watcher.unsubscribe_all()
        self.matrix.remove_handler(self._on_matrix_changed)

        parent = self.parent
        if parent:
            self.parent.matrix_i2c.remove_handler(self._on_matrix_changed)

        diagram = self.diagram
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

    def _on_parent_changed(self, event):
        old_parent = event.old_value
        if old_parent:
            old_parent.matrix_i2c.remove_handler(self._on_matrix_changed)
            m = old_parent.matrix_i2c
            self.matrix.set(*self.matrix.multiply(m))

        new_parent = event.new_value
        if new_parent:
            new_parent.matrix_i2c.add_handler(self._on_matrix_changed)
            m = new_parent.matrix_i2c.inverse()
            self.matrix.set(*self.matrix.multiply(m))

    def _on_matrix_changed(self, matrix, old_value):
        if self.parent:
            self.matrix_i2c.set(*(self.matrix * self.parent.matrix_i2c))
        else:
            self.matrix_i2c.set(*self.matrix)
        self.request_update()
        if matrix is self.matrix:
            self.handle(MatrixUpdated(self, old_value))


Element.presentation = association(
    "presentation", Presentation, composite=True, opposite="subject"
)
Presentation.parent = association("parent", Presentation, upper=1, opposite="children")
Presentation.children = association(
    "children", Presentation, composite=True, opposite="parent"
)


class MatrixUpdated(RevertibeEvent):
    def __init__(self, element, old_value):
        super().__init__(element)
        self.old_value = old_value

    def revert(self, target):
        target.matrix.set(*self.old_value)
