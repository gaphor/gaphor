"""Base code for presentation elements."""

from __future__ import annotations

import ast
import logging
from typing import TYPE_CHECKING, Generic, TypeVar

from gaphas.item import Matrices

from gaphor.core.modeling.element import Element, Id, UnlinkEvent
from gaphor.core.modeling.event import RevertibeEvent
from gaphor.core.modeling.properties import relation_many, relation_one

if TYPE_CHECKING:
    from gaphor.core.modeling.diagram import Diagram

S = TypeVar("S", bound=Element)


log = logging.getLogger(__name__)


class Presentation(Matrices, Element, Generic[S]):
    """This presentation is used to link the behaviors of
    `gaphor.core.modeling` and `gaphas.Item`."""

    def __init__(self, diagram: Diagram, id: Id | None = None) -> None:
        super().__init__(id=id, model=diagram.model)
        self.diagram = diagram
        self._original_diagram = diagram

        def update(event):
            if self.diagram:
                self.diagram.request_update(self)

        self._watcher = self.watcher(default_handler=update)
        self.watch("subject")
        self.watch("children")
        self.watch("diagram", self._on_diagram_changed)
        self.watch("parent", self._on_parent_changed)
        self.matrix.add_handler(self._on_matrix_changed)

    subject: relation_one[S]
    diagram: relation_one[Diagram]
    parent: relation_one[Presentation]
    children: relation_many[Presentation]

    def request_update(self):
        if self.diagram:
            self.diagram.request_update(self)

    def watch(self, path, handler=None):
        """Watch a certain path of elements starting with the DiagramItem. The
        handler is optional and will default to a simple self.request_update().

        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent(returns self).
        """
        self._watcher.watch(path, handler)
        return self

    def change_parent(self, new_parent):
        """Change the parent and update the item's matrix so the item visualy
        remains in the same place."""
        old_parent = self.parent
        if new_parent is old_parent:
            return

        self.parent = new_parent
        m = self.matrix
        if old_parent:
            m = m * old_parent.matrix_i2c
        if new_parent:
            m = m * new_parent.matrix_i2c.inverse()
        self.matrix.set(*m)

    def load(self, name, value):
        if name == "matrix":
            self.matrix.set(*ast.literal_eval(value))
        elif name == "parent":
            if self.parent and self.parent is not value:
                raise ValueError(f"Parent can not be set twice on {self}")
            super().load(name, value)
            self.parent.matrix_i2c.add_handler(self._on_matrix_changed)
            self._on_matrix_changed(None, ())
        else:
            super().load(name, value)

    def unlink(self):
        """Remove the item from the diagram and set subject to None."""
        self.inner_unlink(UnlinkEvent(self, diagram=self._original_diagram))

    def inner_unlink(self, unlink_event: UnlinkEvent) -> None:
        self._watcher.unsubscribe_all()
        self.matrix.remove_handler(self._on_matrix_changed)

        parent = self.parent
        if parent:
            self.parent.matrix_i2c.remove_handler(self._on_matrix_changed)

        diagram = unlink_event.diagram
        if diagram:
            diagram.connections.remove_connections_to_item(self)
        super().inner_unlink(unlink_event)

    def _on_diagram_changed(self, event):
        new_value = event.new_value
        if new_value and new_value is not self._original_diagram:
            self.diagram = self._original_diagram
            raise ValueError("Can not change diagram for a presentation")

    def _on_parent_changed(self, event):
        old_parent = event.old_value
        if old_parent:
            old_parent.matrix_i2c.remove_handler(self._on_matrix_changed)

        new_parent = event.new_value
        if new_parent:
            new_parent.matrix_i2c.add_handler(self._on_matrix_changed)

        self._on_matrix_changed(None, ())

    def _on_matrix_changed(self, matrix, old_value):
        if self.parent:
            self.matrix_i2c.set(*(self.matrix * self.parent.matrix_i2c))
        else:
            self.matrix_i2c.set(*self.matrix)
        self.request_update()
        if matrix is self.matrix:
            self.handle(MatrixUpdated(self, old_value))


class MatrixUpdated(RevertibeEvent):
    def __init__(self, element, old_value):
        super().__init__(element)
        self.old_value = old_value

    def revert(self, target):
        target.matrix.set(*self.old_value)
