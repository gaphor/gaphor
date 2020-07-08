"""This module contains a model element Diagram. Diagrams
can be visualized and edited.

The DiagramCanvas class extends the gaphas.Canvas class.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import gaphas

from gaphor.core.modeling.coremodel import PackageableElement
from gaphor.core.modeling.element import Id, RepositoryProtocol
from gaphor.core.modeling.event import DiagramItemCreated
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.core.styling.properties import DEFAULT_STYLE, Style

if TYPE_CHECKING:
    from cairo import Context as CairoContext
    from gaphor.core.modeling.properties import relation_one
    from gaphor.UML import Package

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateContext:
    """
    Context used when updating items (Presentation's).

    Style contains the base style, no style alterations due to view state
    (focused, hovered, etc.).
    """

    style: Style


@dataclass(frozen=True)
class DrawContext:
    """
    Special context for draw()'ing the item. The draw-context contains
    stuff like the cairo context and flags like selected and
    focused.
    """

    cairo: CairoContext
    style: Style
    selected: bool
    focused: bool
    hovered: bool
    dropzone: bool


class DiagramCanvas(gaphas.Canvas):
    """DiagramCanvas extends the gaphas.Canvas class.  Updates to the canvas
    can be blocked by setting the block_updates property to true.  A save
    function can be applied to all root canvas items.  Canvas items can be
    selected with an optional expression filter."""

    def __init__(self, diagram, create_update_context):
        """Initialize the diagram canvas with the supplied diagram.  By default,
        updates are not blocked."""

        super().__init__(create_update_context)
        self._diagram = diagram
        self._block_updates = False

    diagram = property(lambda s: s._diagram)

    def _set_block_updates(self, block):
        """Sets the block_updates property.  If false, the diagram canvas is
        updated immediately."""

        self._block_updates = block
        if not block:
            self.update_now()

    block_updates = property(lambda s: s._block_updates, _set_block_updates)

    def update_now(self):
        """Update the diagram canvas, unless block_updates is true."""

        if self._block_updates:
            return
        super().update_now()

    def save(self, save_func):
        """Apply the supplied save function to all root diagram items."""

        for item in self.get_root_items():
            save_func(item)

    def postload(self):
        """Called after the diagram canvas has loaded.  Currently does nothing.
        """

    def select(self, expression=lambda e: True):
        """Return a list of all canvas items that match expression."""

        return list(filter(expression, self.get_all_items()))

    def reparent(self, item, parent):
        """A more fancy version of the reparent method."""
        old_parent = self.get_parent(item)

        if old_parent:
            super().reparent(item, None)
            m = self.get_matrix_i2c(old_parent)
            item.matrix *= m
            old_parent.request_update()

        if parent:
            super().reparent(item, parent)
            m = self.get_matrix_c2i(parent)
            item.matrix *= m
            parent.request_update()


class Diagram(PackageableElement):
    """Diagrams may contain model elements and can be owned by a Package.
    """

    package: relation_one[Package]

    def __init__(
        self, id: Optional[Id] = None, model: Optional[RepositoryProtocol] = None
    ):
        """Initialize the diagram with an optional id and element model.
        The diagram also has a canvas."""

        super().__init__(id, model)
        self.canvas = DiagramCanvas(self, self._create_update_context)

    @property
    def styleSheet(self) -> Optional[StyleSheet]:
        return next(self._model.select(StyleSheet), None) if self._model else None

    def item_style(self, item) -> Style:
        styleSheet = self.styleSheet
        return (
            styleSheet.item_style(item)  # type: ignore[misc]
            if styleSheet
            else DEFAULT_STYLE
        )

    def _create_update_context(self, item):
        return UpdateContext(style=self.item_style(item))

    def save(self, save_func):
        """Apply the supplied save function to this diagram and the canvas."""

        super().save(save_func)
        save_func("canvas", self.canvas)

    def postload(self):
        """Handle post-load functionality for the diagram canvas."""
        super().postload()
        self.canvas.postload()

    def create(self, type, parent=None, subject=None):
        """Create a new canvas item on the canvas. It is created with
        a unique ID and it is attached to the diagram's root item.  The type
        parameter is the element class to create.  The new element also has an
        optional parent and subject."""

        return self.create_as(type, str(uuid.uuid1()), parent, subject)

    def create_as(self, type, id, parent=None, subject=None):
        if not (type and issubclass(type, gaphas.Item)):
            raise TypeError(
                f"Type {type} can not be added to a diagram as it is not a diagram item"
            )
        item = type(id, self.model)
        if subject:
            item.subject = subject
        self.canvas.add(item, parent)
        self.model.handle(DiagramItemCreated(self.model, item))
        return item

    def lookup(self, id):
        for item in self.canvas.get_all_items():
            if item.id == id:
                return item

    def unlink(self):
        """Unlink all canvas items then unlink this diagram."""

        for item in self.canvas.get_all_items():
            try:
                item.unlink()
            except (AttributeError, KeyError):
                pass

        super().unlink()
