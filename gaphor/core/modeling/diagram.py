"""This module contains a model element Diagram.

Diagrams can be visualized and edited.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Iterable, Iterator, Optional, Sequence, Set, Union

import gaphas

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.coremodel import Element, PackageableElement
from gaphor.core.modeling.element import Id, RepositoryProtocol
from gaphor.core.modeling.event import AssociationDeleted, DiagramItemCreated
from gaphor.core.modeling.presentation import Presentation
from gaphor.core.modeling.properties import association, relation_many, relation_one
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.core.styling import Style, StyleNode

if TYPE_CHECKING:
    from gaphor.UML import Package

log = logging.getLogger(__name__)


# Not all styles are requires: "background-color", "font-weight",
# "text-color", and "text-decoration" are optional (can default to None)
FALLBACK_STYLE: Style = {
    "color": (0, 0, 0, 1),
    "font-family": "sans",
    "font-size": 14,
    "line-width": 2,
    "padding": (0, 0, 0, 0),
}


@dataclass(frozen=True)
class UpdateContext:
    """Context used when updating items (Presentation's).

    Style contains the base style, no style alterations due to view
    state (focus, hover, etc.).
    """

    style: Style


@dataclass(frozen=True)
class DrawContext:
    """Special context for draw()'ing the item.

    The draw-context contains stuff like the cairo context and flags
    like selected and focused.
    """

    cairo: gaphas.types.CairoContext
    style: Style
    selected: bool
    focused: bool
    hovered: bool
    dropzone: bool


# From https://www.python.org/dev/peps/pep-0616/
def removesuffix(self: str, suffix: str) -> str:
    # suffix='' should not call self[:-0].
    if suffix and self.endswith(suffix):
        return self[: -len(suffix)]
    else:
        return self[:]


@lru_cache()
def attrname(obj, lower_name):
    """Look up a real attribute name based on a lower case (normalized)
    name."""
    for name in dir(obj):
        if name.lower() == lower_name:
            return name
    return lower_name


def rgetattr(obj, names):
    """Recursively het a name, based on a list of names."""
    name, *tail = names
    v = getattr(obj, attrname(obj, name), None)
    if isinstance(v, (collection, list, tuple)):
        if tail:
            for m in v:
                yield from rgetattr(m, tail)
        else:
            yield from v
    else:
        if tail:
            yield from rgetattr(v, tail)
        elif v is not None:
            yield v


def attrstr(obj):
    """Returns lower-case string representation of an attribute."""
    if isinstance(obj, str):
        return obj.lower()
    elif isinstance(obj, (bool, int)):
        return "true" if obj else ""
    elif isinstance(obj, Element):
        return obj.__class__.__name__.lower()
    log.warn(
        f'Can not make a string out of {obj}, returning "". Please raise an issue.'
    )
    return ""


class StyledDiagram:
    def __init__(
        self, diagram: Diagram, selection: Optional[gaphas.view.Selection] = None
    ):
        self.diagram = diagram
        self.selection = selection or gaphas.view.Selection()

    def name(self) -> str:
        return "diagram"

    def parent(self):
        return None

    def children(self) -> Iterator[StyledItem]:
        return (
            StyledItem(item, self.selection)
            for item in self.diagram.get_all_items()
            if not item.parent
        )

    def attribute(self, name: str) -> str:
        fields = name.split(".")
        return " ".join(map(attrstr, rgetattr(self.diagram, fields))).strip()

    def state(self):
        return ()


class StyledItem:
    """Wrapper to allow style information to be retrieved.

    For convenience, a selection can be added. The selection instance
    will provide pseudo-classes for the item (focus, hover, etc.).
    """

    def __init__(
        self, item: Presentation, selection: Optional[gaphas.view.Selection] = None
    ):
        assert item.diagram
        self.item = item
        self.diagram = item.diagram
        self.selection = selection

    def name(self) -> str:
        return removesuffix(type(self.item).__name__, "Item").lower()

    def parent(self) -> Union[StyledItem, StyledDiagram]:
        parent = self.item.parent
        return (
            StyledItem(parent, self.selection)
            if parent
            else StyledDiagram(self.diagram, self.selection)
        )

    def children(self) -> Iterator[StyledItem]:
        selection = self.selection
        return (StyledItem(child, selection) for child in self.item.children)

    def attribute(self, name: str) -> str:
        fields = name.split(".")
        a = " ".join(map(attrstr, rgetattr(self.item, fields))).strip()
        if (not a) and self.item.subject:
            a = " ".join(map(attrstr, rgetattr(self.item.subject, fields))).strip()
        return a

    def state(self) -> Sequence[str]:
        item = self.item
        selection = self.selection
        return (
            (
                "active" if item in selection.selected_items else "",
                "focus" if item is selection.focused_item else "",
                "hover" if item is selection.hovered_item else "",
                "drop" if item is selection.dropzone_item else "",
                "disabled" if item in selection.grayed_out_items else "",
            )
            if selection
            else ()
        )


class PseudoCanvas:
    """A "pseudo" canvas implementation, for storing items."""

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    def save(self, save_func):
        for item in self.diagram.ownedPresentation:
            if not item.parent:
                save_func(item)


class Diagram(PackageableElement):
    """Diagrams may contain model elements and can be owned by a Package."""

    package: relation_one[Package]

    def __init__(
        self, id: Optional[Id] = None, model: Optional[RepositoryProtocol] = None
    ):
        """Initialize the diagram with an optional id and element model.

        The diagram also has a canvas.
        """

        super().__init__(id, model)
        self._connections = gaphas.connections.Connections()
        self._connections.add_handler(self._on_constraint_solved)

        self._registered_views: Set[gaphas.view.model.View] = set()

        self._watcher = self.watcher()
        self._watcher.watch("ownedPresentation", self._presentation_removed)

        # Record all items changed during constraint solving,
        # so their `post_update()` method can be called.
        self._resolved_items: Set[gaphas.item.Item] = set()

    ownedPresentation: relation_many[Presentation] = association(
        "ownedPresentation", Presentation, composite=True, opposite="diagram"
    )

    def _presentation_removed(self, event):
        if isinstance(event, AssociationDeleted) and event.old_value:
            self._update_views(removed_items=(event.old_value,))

    @property
    def styleSheet(self) -> Optional[StyleSheet]:
        return next(self.model.select(StyleSheet), None)

    def style(self, node: StyleNode) -> Style:
        style_sheet = self.styleSheet
        return style_sheet.match(node) if style_sheet else FALLBACK_STYLE

    def save(self, save_func):
        """Apply the supplied save function to this diagram and the canvas."""

        super().save(save_func)
        save_func("canvas", PseudoCanvas(self))

    def postload(self):
        """Handle post-load functionality for the diagram."""
        super().postload()

    def create(self, type, parent=None, subject=None):
        """Create a new diagram item on the diagram.

        It is created with a unique ID and it is attached to the
        diagram's root item.  The type parameter is the element class to
        create.  The new element also has an optional parent and
        subject.
        """

        return self.create_as(type, str(uuid.uuid1()), parent, subject)

    def create_as(self, type, id, parent=None, subject=None):
        if not (type and issubclass(type, Presentation)):
            raise TypeError(
                f"Type {type} can not be added to a diagram as it is not a diagram item"
            )
        # Avoid events that reference this element before its created-event is emitted.
        with self.model.block_events():
            item = type(diagram=self, id=id)
        assert isinstance(
            item, gaphas.Item
        ), f"Type {type} does not comply with Item protocol"
        self.model.handle(DiagramItemCreated(self, item))
        if subject:
            item.subject = subject
        if parent:
            item.parent = parent
        self.request_update(item)
        return item

    def lookup(self, id):
        for item in self.get_all_items():
            if item.id == id:
                return item

    def unlink(self):
        """Unlink all canvas items then unlink this diagram."""
        for item in self.ownedPresentation:
            self.connections.remove_connections_to_item(item)
        self._watcher.unsubscribe_all()
        super().unlink()

    def select(self, expression=None) -> Iterator[Presentation]:
        """Return a iterator of all canvas items that match expression."""
        if expression is None:
            yield from self.get_all_items()
        elif isinstance(expression, type):
            yield from (e for e in self.get_all_items() if isinstance(e, expression))
        else:
            yield from (e for e in self.get_all_items() if expression(e))

    @property
    def connections(self) -> gaphas.connections.Connections:
        return self._connections

    def get_all_items(self) -> Iterable[Presentation]:
        """Get all items owned by this diagram, ordered depth-first."""

        def iter_children(item):
            for child in item.children:
                yield child
                yield from iter_children(child)

        for root in self.ownedPresentation:
            if not root.parent:
                yield root
                yield from iter_children(root)

    def get_parent(self, item: Presentation) -> Optional[Presentation]:
        return item.parent

    def get_children(self, item: Presentation) -> Iterable[Presentation]:
        return iter(item.children)

    def sort(self, items: Sequence[Presentation]) -> Iterable[Presentation]:
        items_set = set(items)
        return (n for n in self.get_all_items() if n in items_set)

    def request_update(
        self, item: gaphas.item.Item, update: bool = True, matrix: bool = True
    ) -> None:
        if update and matrix:
            self._update_views(dirty_items=(item,), dirty_matrix_items=(item,))
        elif update:
            self._update_views(dirty_items=(item,))
        elif matrix:
            self._update_views(dirty_matrix_items=(item,))

    def _update_views(self, dirty_items=(), dirty_matrix_items=(), removed_items=()):
        """Send an update notification to all registered views."""
        for v in self._registered_views:
            v.request_update(dirty_items, dirty_matrix_items, removed_items)

    @gaphas.decorators.nonrecursive
    def update_now(
        self,
        dirty_items: Sequence[Presentation],
        dirty_matrix_items: Sequence[Presentation] = (),
    ) -> None:
        """Update the diagram canvas."""

        sort = self.sort

        def dirty_items_with_ancestors():
            for item in set(dirty_items):
                yield item
                yield from gaphas.canvas.ancestors(self, item)

        all_dirty_items = list(reversed(list(sort(dirty_items_with_ancestors()))))
        contexts = self._pre_update_items(all_dirty_items)

        self._resolved_items.clear()

        self._connections.solve()

        all_dirty_items.extend(self._resolved_items)
        self._post_update_items(reversed(list(sort(all_dirty_items))), contexts)

    def _pre_update_items(self, items):
        contexts = {}
        for item in items:
            context = UpdateContext(style=self.style(StyledItem(item)))
            item.pre_update(context)
            contexts[item] = context
        return contexts

    def _post_update_items(self, items, contexts):
        for item in items:
            context = contexts.get(item)
            if not context:
                context = UpdateContext(style=self.style(StyledItem(item)))
            item.post_update(context)

    def _on_constraint_solved(self, cinfo: gaphas.connections.Connection) -> None:
        dirty_items = set()
        if cinfo.item:
            dirty_items.add(cinfo.item)
            self._resolved_items.add(cinfo.item)
        if cinfo.connected:
            dirty_items.add(cinfo.connected)
            self._resolved_items.add(cinfo.connected)
        if dirty_items:
            self._update_views(dirty_items)

    def register_view(self, view: gaphas.view.model.View[Presentation]) -> None:
        self._registered_views.add(view)

    def unregister_view(self, view: gaphas.view.model.View[Presentation]) -> None:
        self._registered_views.discard(view)


Presentation.diagram = association(
    "diagram", Diagram, upper=1, opposite="ownedPresentation"
)
