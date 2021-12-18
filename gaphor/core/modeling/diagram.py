"""This module contains a model element Diagram.

Diagrams can be visualized and edited.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import (
    Callable,
    Iterable,
    Iterator,
    Protocol,
    Sequence,
    TypeVar,
    overload,
    runtime_checkable,
)

import gaphas
from cairo import Context as CairoContext

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.element import Element, Id, RepositoryProtocol
from gaphor.core.modeling.event import AssociationAdded, AssociationDeleted
from gaphor.core.modeling.presentation import Presentation
from gaphor.core.modeling.properties import (
    association,
    attribute,
    relation_many,
    relation_one,
)
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.core.styling import Style, StyleNode

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

    cairo: CairoContext
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
    elif tail:
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


def qualifiedName(element: Element) -> list[str]:
    """Returns the qualified name of the element as a tuple."""
    name: str = getattr(element, "name", "??")
    if element.owner:
        return qualifiedName(element.owner) + [name]
    else:
        return [name]


class StyledDiagram:
    def __init__(
        self, diagram: Diagram, selection: gaphas.selection.Selection | None = None
    ):
        self.diagram = diagram
        self.selection = selection or gaphas.selection.Selection()

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
        self, item: Presentation, selection: gaphas.selection.Selection | None = None
    ):
        assert item.diagram
        self.item = item
        self.diagram = item.diagram
        self.selection = selection

    def name(self) -> str:
        return removesuffix(type(self.item).__name__, "Item").lower()

    def parent(self) -> StyledItem | StyledDiagram:
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


P = TypeVar("P", bound=Presentation)


class Diagram(Element):
    """Diagrams may contain model elements and can be owned by a Package."""

    name: attribute[str] = attribute("name", str)
    diagramType: attribute[str] = attribute("diagramType", str)
    element: relation_one[Element]

    def __init__(self, id: Id | None = None, model: RepositoryProtocol | None = None):
        """Initialize the diagram with an optional id and element model.

        The diagram also has a canvas.
        """

        super().__init__(id, model)
        self._connections = gaphas.connections.Connections()
        self._connections.add_handler(self._on_constraint_solved)

        self._registered_views: set[gaphas.model.View] = set()

        self._watcher = self.watcher()
        self._watcher.watch("ownedPresentation", self._owned_presentation_changed)
        self._watcher.watch("ownedPresentation.parent", self._order_owned_presentation)

    ownedPresentation: relation_many[Presentation] = association(
        "ownedPresentation", Presentation, composite=True, opposite="diagram"
    )

    @property
    def qualifiedName(self) -> list[str]:
        """Returns the qualified name of the element as a tuple."""
        return qualifiedName(self)

    def _owned_presentation_changed(self, event):
        if isinstance(event, AssociationDeleted) and event.old_value:
            self._update_views(removed_items=(event.old_value,))
        elif isinstance(event, AssociationAdded):
            self._order_owned_presentation()

    def _order_owned_presentation(self, event=None):
        if event and event.property is not Presentation.parent:
            return

        ownedPresentation = self.ownedPresentation

        def traverse_items(parent=None) -> Iterable[Presentation]:
            for item in ownedPresentation:
                if item.parent is parent:
                    yield item
                    yield from traverse_items(item)

        new_order = sorted(
            traverse_items(), key=lambda e: int(isinstance(e, gaphas.Line))
        )
        self.ownedPresentation.order(new_order.index)

    @property
    def styleSheet(self) -> StyleSheet | None:
        return next(self.model.select(StyleSheet), None)

    def style(self, node: StyleNode) -> Style:
        style_sheet = self.styleSheet
        return style_sheet.match(node) if style_sheet else FALLBACK_STYLE

    def save(self, save_func):
        """Apply the supplied save function to this diagram and the canvas."""

        super().save(save_func)

    def postload(self):
        """Handle post-load functionality for the diagram."""
        self._order_owned_presentation()
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
        assert isinstance(self.model, PresentationRepositoryProtocol)
        item = self.model.create_as(type, id, diagram=self)
        if not isinstance(item, gaphas.Item):
            raise TypeError(f"Type {type} does not comply with Item protocol")
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

    @overload
    def select(
        self, expression: Callable[[Presentation], bool]
    ) -> Iterator[Presentation]:
        ...

    @overload
    def select(self, expression: type[P]) -> Iterator[P]:
        ...

    @overload
    def select(self, expression: None) -> Iterator[Presentation]:
        ...

    def select(self, expression=None):
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
        yield from self.ownedPresentation

    def get_parent(self, item: Presentation) -> Presentation | None:
        return item.parent

    def get_children(self, item: Presentation) -> Iterable[Presentation]:
        return iter(item.children)

    def sort(self, items: Sequence[Presentation]) -> Iterable[Presentation]:
        items_set = set(items)
        return (n for n in self.get_all_items() if n in items_set)

    def request_update(self, item: gaphas.item.Item) -> None:
        if item in self.ownedPresentation:
            self._update_views(dirty_items=(item,))

    def _update_views(self, dirty_items=(), removed_items=()):
        """Send an update notification to all registered views."""
        for v in self._registered_views:
            v.request_update(dirty_items, removed_items)

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
        self._update_items(all_dirty_items)

        self._connections.solve()

    def _update_items(self, items):
        for item in items:
            update = getattr(item, "update", None)
            if update:
                update(UpdateContext(style=self.style(StyledItem(item))))

    def _on_constraint_solved(self, cinfo: gaphas.connections.Connection) -> None:
        dirty_items = set()
        if cinfo.item:
            dirty_items.add(cinfo.item)
        if cinfo.connected:
            dirty_items.add(cinfo.connected)
        if dirty_items:
            self._update_views(dirty_items)

    def register_view(self, view: gaphas.model.View[Presentation]) -> None:
        self._registered_views.add(view)

    def unregister_view(self, view: gaphas.model.View[Presentation]) -> None:
        self._registered_views.discard(view)


@runtime_checkable
class PresentationRepositoryProtocol(Protocol):
    def create_as(self, type: type[P], id: str, diagram: Diagram) -> P:
        ...
