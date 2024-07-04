"""This module contains a model element Diagram.

Diagrams can be visualized and edited.
"""
from __future__ import annotations

import logging
from collections.abc import Callable, Collection, Iterable, Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import (
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

import gaphas
from cairo import Context as CairoContext

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.element import (
    Element,
    Id,
    RepositoryProtocol,
    generate_id,
)
from gaphor.core.modeling.event import (
    AssociationAdded,
    AssociationDeleted,
    DiagramUpdateRequested,
)
from gaphor.core.modeling.presentation import Presentation
from gaphor.core.modeling.properties import (
    association,
    attribute,
    relation_many,
    relation_one,
)
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.core.styling import CompiledStyleSheet, Style, StyleNode
from gaphor.i18n import translation

log = logging.getLogger(__name__)

# Not all styles are required: "background-color", "font-weight",
# "text-color", and "text-decoration" are optional (can default to None)
FALLBACK_STYLE: Style = {
    "color": (0, 0, 0, 1),
    "font-family": "sans",
    "font-size": 14,
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


@lru_cache()
def attrname(obj, lower_name):
    """Look up a real attribute name based on a lower case (normalized)
    name."""
    return next((name for name in dir(obj) if name.lower() == lower_name), lower_name)


NO_ATTR = object()


def rgetattr(obj, names):
    """Recursively get a name, based on a list of names."""
    name, *tail = names
    v = getattr(obj, attrname(obj, name), NO_ATTR)
    if isinstance(v, (collection, list, tuple)):
        if tail and not v:
            yield NO_ATTR
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


def lookup_attribute(element: Element, name: str) -> str | None:
    """Look up an attribute from an element.

    Attributes can be nested, e.g. ``owner.name``.

    Returns ``""`` if the value is empty,
    ``None`` if the attribute does not exist.
    """
    fields = name.split(".")
    values = list(rgetattr(element, fields))
    attr_values = [v for v in values if v is not NO_ATTR]
    if not attr_values and NO_ATTR in values:
        return None
    return " ".join(map(attrstr, attr_values)).strip()


class StyledDiagram:
    def __init__(
        self,
        diagram: Diagram,
        selection: gaphas.selection.Selection | None = None,
        dark_mode: bool | None = None,
    ):
        self.diagram = diagram
        self.selection = selection
        self.pseudo: str | None = None
        self.dark_mode = dark_mode

    def name(self) -> str:
        return "diagram"

    def parent(self) -> StyleNode | None:
        return None

    def children(self) -> Iterator[StyleNode]:
        return (
            StyledItem(item, self.selection, dark_mode=self.dark_mode)
            for item in self.diagram.get_all_items()
            if not item.parent
        )

    def attribute(self, name: str) -> str | None:
        return lookup_attribute(self.diagram, name)

    def state(self) -> Sequence[str]:
        return ()

    def __hash__(self):
        return hash((self.diagram, self.state(), self.dark_mode))

    def __eq__(self, other):
        return (
            isinstance(other, StyledDiagram)
            and self.diagram == other.diagram
            and self.state() == other.state()
            and self.dark_mode == other.dark_mode
        )


class StyledItem:
    """Wrapper to allow style information to be retrieved.

    For convenience, a selection can be added. The selection instance
    will provide pseudo-classes for the item (focus, hover, etc.).
    """

    def __init__(
        self,
        item: Presentation,
        selection: gaphas.selection.Selection | None = None,
        dark_mode: bool | None = None,
    ):
        assert item.diagram
        self.item = item
        self.diagram = item.diagram
        self.selection = selection
        self.pseudo: str | None = None
        self.dark_mode = dark_mode
        self._state = (
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

    def name(self) -> str:
        return type(self.item).__name__.removesuffix("Item").lower()

    def parent(self) -> StyleNode | None:
        parent = self.item.parent
        return (
            StyledItem(parent, self.selection, dark_mode=self.dark_mode)
            if parent
            else StyledDiagram(self.diagram, self.selection, self.dark_mode)
        )

    def children(self) -> Iterator[StyleNode]:
        item = self.item
        yield from (node.style_node(self) for node in item.css_nodes())

        selection = self.selection
        yield from (
            StyledItem(child, selection, dark_mode=self.dark_mode)
            for child in item.children
        )

    def attribute(self, name: str) -> str | None:
        a = lookup_attribute(self.item, name)
        if a in (None, "") and self.item.subject:
            a = lookup_attribute(self.item.subject, name)
        return a

    def state(self) -> Sequence[str]:
        return self._state

    def __hash__(self):
        return hash((self.item, self.state(), self.dark_mode))

    def __eq__(self, other):
        return (
            isinstance(other, StyledItem)
            and self.item == other.item
            and self.state() == other.state()
            and self.dark_mode == other.dark_mode
        )


P = TypeVar("P", bound=Presentation)


class Diagram(Element):
    """Diagrams may contain :obj:`Presentation` elements and can be owned by any element."""

    diagramType: attribute[str] = attribute("diagramType", str)
    element: relation_one[Element]

    def __init__(self, id: Id | None = None, model: RepositoryProtocol | None = None):
        """Initialize the diagram with an optional id and element model."""

        super().__init__(id, model)
        self._connections = gaphas.connections.Connections()
        self._connections.add_handler(self._on_constraint_solved)

        self._compiled_style_sheet: CompiledStyleSheet | None = None
        self._registered_views: set[gaphas.model.View] = set()
        self._dirty_items: set[gaphas.Item] = set()

        self._watcher = self.watcher()
        self._watcher.watch("ownedPresentation", self._owned_presentation_changed)
        self._watcher.watch("ownedPresentation.parent", self._order_owned_presentation)

    ownedPresentation: relation_many[Presentation] = association(
        "ownedPresentation", Presentation, composite=True, opposite="diagram"
    )

    def _owned_presentation_changed(self, event):
        if isinstance(event, AssociationDeleted) and event.old_value:
            self._update_dirty_items(removed_items={event.old_value})
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
        if not (compiled_style_sheet := self._compiled_style_sheet):
            style_sheet = self.styleSheet
            compiled_style_sheet = self._compiled_style_sheet = (
                style_sheet.new_compiled_style_sheet() if style_sheet else None
            )

        return (
            compiled_style_sheet.compute_style(node)
            if compiled_style_sheet
            else FALLBACK_STYLE
        )

    def gettext(self, message: str) -> str:
        """Translate a message to the language used in the model."""
        style_sheet = self.styleSheet
        if style_sheet and style_sheet.naturalLanguage:
            return translation(style_sheet.naturalLanguage).gettext(message)
        return message

    def postload(self):
        """Handle post-load functionality for the diagram."""
        self._order_owned_presentation()
        super().postload()

    def create(
        self,
        type_: type[P],
        parent: Presentation | None = None,
        subject: Element | None = None,
    ) -> P:
        """Create a new diagram item on the diagram.

        It is created with a unique ID, and it is attached to the
        diagram's root item.  The type parameter is the element class to
        create.  The new element also has an optional parent and
        subject.
        """

        return self.create_as(type_, generate_id(), parent, subject)

    def create_as(
        self,
        type_: type[P],
        id: Id,
        parent: Presentation | None = None,
        subject: Element | None = None,
    ) -> P:
        assert isinstance(self.model, PresentationRepositoryProtocol)
        item = self.model.create_as(type_, id, diagram=self)
        if not isinstance(item, gaphas.Item):
            raise TypeError(f"Type {type_} does not comply with Item protocol")
        if subject:
            item.subject = subject
        if parent:
            item.parent = parent
        self.update({item})
        return item

    def lookup(self, id: Id) -> Presentation | None:
        """Find a presentation item by id.

        Returns a presentation in this diagram or return ``None``.
        """
        return next((item for item in self.get_all_items() if item.id == id), None)

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
        """Return an iterator of all canvas items that match expression."""
        if expression is None:
            yield from self.get_all_items()
        elif isinstance(expression, type):
            yield from (e for e in self.get_all_items() if isinstance(e, expression))
        else:
            yield from (e for e in self.get_all_items() if expression(e))

    def update(self, dirty_items: Collection[Presentation] = ()) -> None:
        """Update the diagram.

        All items that requested an update via :meth:`request_update`
        are now updates. If an item has an ``update(context: UpdateContext)``
        method, it's invoked. Constraints are solved.
        """
        self._update_dirty_items(dirty_items)

        # Clear our (cached) style sheet first
        self._compiled_style_sheet = None

        def dirty_items_with_ancestors():
            for item in self._dirty_items:
                yield item
                yield from gaphas.canvas.ancestors(self, item)

        for item in reversed(list(self.sort(dirty_items_with_ancestors()))):
            if update := getattr(item, "update", None):
                update(UpdateContext(style=self.style(StyledItem(item))))

        self._connections.solve()

        self._dirty_items.clear()

    # gaphas.model.Model protocol:

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
        """Schedule an item for updating.

        No update is done at this point, it's only added to the set of
        to-be updated items.

        This method is part of the :obj:`gaphas.model.Model` protocol.
        """
        if item in self.ownedPresentation:
            self._update_dirty_items(dirty_items={item})

    def update_now(self, _dirty_items: Collection[Presentation]) -> None:
        pass

    def register_view(self, view: gaphas.model.View[Presentation]) -> None:
        self._registered_views.add(view)

    def unregister_view(self, view: gaphas.model.View[Presentation]) -> None:
        self._registered_views.discard(view)

    def _update_dirty_items(self, dirty_items=(), removed_items=()):
        """Send an update notification to all registered views."""
        should_emit = not bool(self._dirty_items)

        if dirty_items:
            self._dirty_items.update(dirty_items)
        if removed_items:
            self._dirty_items.difference_update(removed_items)

        if should_emit:
            self.handle(DiagramUpdateRequested(self))

        # We can directly request updates on the view, since those happen asynchronously
        for v in self._registered_views:
            v.request_update(dirty_items, removed_items)

    def _on_constraint_solved(self, cinfo: gaphas.connections.Connection) -> None:
        dirty_items = set()
        if cinfo.item:
            dirty_items.add(cinfo.item)
        if cinfo.connected:
            dirty_items.add(cinfo.connected)
        if dirty_items:
            self._update_dirty_items(dirty_items)


@runtime_checkable
class PresentationRepositoryProtocol(Protocol):
    def create_as(self, type: type[P], id: str, diagram: Diagram) -> P:
        ...
