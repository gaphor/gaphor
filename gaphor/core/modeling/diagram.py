"""This module contains a model element Diagram. Diagrams can be visualized and
edited.

The DiagramCanvas class extends the gaphas.Canvas class.
"""
from __future__ import annotations

import logging
import textwrap
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    Optional,
    Reversible,
    Sequence,
    Union,
)

import gaphas

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.coremodel import Element, PackageableElement
from gaphor.core.modeling.element import Id, RepositoryProtocol
from gaphor.core.modeling.event import DiagramItemCreated
from gaphor.core.modeling.presentation import Presentation
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.core.styling import Style, StyleNode

if TYPE_CHECKING:
    from cairo import Context as CairoContext

    from gaphor.core.modeling.properties import relation_one
    from gaphor.UML import Package

log = logging.getLogger(__name__)


# Not all styles are requires: "background-color", "font-weight",
# "text-color", and "text-decoration" are optional (can default to None)
FALLBACK_STYLE: Style = {
    "color": (0, 0, 0, 1),
    "font-family": "sans",
    "font-size": 14,
    "highlight-color": (0, 0, 1, 0.4),
    "line-width": 2,
    "padding": (0, 0, 0, 0),
}


DEFAULT_STYLE_SHEET = textwrap.dedent(
    """\
    * {
     background-color: transparent;
     color: black;
     font-family: sans;
     font-size: 14;
     highlight-color: rgba(0, 0, 255, 0.4);
     line-width: 2;
     padding: 0;
    }

    diagram {
     background-color: white;
     line-style: normal;
     /* line-style: sloppy 0.3; */
    }
    """
)


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
            for item in self.diagram.canvas.get_root_items()
        )

    def attribute(self, name: str) -> str:
        fields = name.split(".")
        return " ".join(map(attrstr, rgetattr(self.diagram, fields))).strip()

    def state(self):
        return ()


class StyledItem:
    """Wrapper to allow style information to be retrieved.

    For convenience, a view can be added. The view will provide pseudo-
    classes for the item (focus, hover, etc.)
    """

    def __init__(
        self, item: Presentation, selection: Optional[gaphas.view.Selection] = None
    ):
        assert item.canvas
        self.item = item
        self.canvas = item.canvas
        self.selection = selection or gaphas.view.Selection()

    def name(self) -> str:
        return removesuffix(type(self.item).__name__, "Item").lower()

    def parent(self) -> Union[StyledItem, StyledDiagram]:
        parent = self.canvas.get_parent(self.item)
        return (
            StyledItem(parent, self.selection)
            if parent
            else StyledDiagram(self.item.diagram, self.selection)
        )

    def children(self) -> Iterator[StyledItem]:
        children = self.canvas.get_children(self.item)
        selection = self.selection
        return (StyledItem(child, selection) for child in children)

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
            "active" if item in selection.selected_items else "",
            "focus" if item is selection.focused_item else "",
            "hover" if item is selection.hovered_item else "",
            "drop" if item is selection.dropzone_item else "",
        )


class DiagramCanvas(gaphas.Canvas):
    """DiagramCanvas extends the gaphas.Canvas class.

    Updates to the canvas can be blocked by setting the block_updates
    property to true.  A save function can be applied to all root canvas
    items.  Canvas items can be selected with an optional expression
    filter.
    """

    def __init__(self, diagram: Diagram):
        """Initialize the diagram canvas with the supplied diagram.

        By default, updates are not blocked.
        """

        super().__init__()
        self._diagram = diagram
        self._block_updates = False

    diagram = property(lambda s: s._diagram)

    @gaphas.state.observed
    def add(self, item, parent=None, index=None):
        assert item not in self._tree.nodes, f"Adding already added node {item}"
        self._tree.add(item, parent, index)
        item.canvas = self
        self.request_update(item)

    @gaphas.state.observed
    def _remove(self, item):
        """Remove is done in a separate, @observed, method so the undo system
        can restore removed items in the right order."""
        item.canvas = None
        self._tree.remove(item)
        self._connections.disconnect_item(self)
        self._update_views(removed_items=(item,))

    gaphas.state.reversible_pair(
        add,
        _remove,
        bind1={
            "parent": lambda self, item: self.get_parent(item),
            "index": lambda self, item: self._tree.get_siblings(item).index(item),
        },
    )

    @property
    def block_updates(self) -> bool:
        return self._block_updates

    @block_updates.setter
    def block_updates(self, block: bool) -> None:
        """Sets the block_updates property.

        If false, the diagram canvas is updated immediately.
        """
        self._block_updates = block

    @gaphas.decorators.nonrecursive
    def update_now(self, dirty_items, dirty_matrix_items=()):
        """Update the diagram canvas, unless block_updates is true."""

        if self._block_updates:
            return

        sort = self.sort

        def dirty_items_with_ancestors():
            for item in set(dirty_items):
                yield item
                yield from self._tree.get_ancestors(item)

        all_dirty_items = list(reversed(list(sort(dirty_items_with_ancestors()))))

        contexts = self._pre_update_items(all_dirty_items)

        super().update_now(dirty_items, dirty_matrix_items)

        self._post_update_items(all_dirty_items, contexts)

    def _pre_update_items(self, items):
        diagram = self.diagram

        contexts = {}
        for item in items:
            context = UpdateContext(style=diagram.style(StyledItem(item)))
            item.pre_update(context)
            contexts[item] = context
        return contexts

    def _post_update_items(self, items, contexts):
        diagram = self.diagram
        for item in items:
            context = contexts.get(item)
            if not context:
                context = UpdateContext(style=diagram.style(StyledItem(item)))
            item.post_update(context)

    def save(self, save_func):
        """Apply the supplied save function to all root diagram items."""

        for item in self.get_root_items():
            save_func(item)

    def postload(self):
        """Called after the diagram canvas has loaded.

        Currently does nothing.
        """

    def select(self, expression=lambda e: True):
        """Return a list of all canvas items that match expression."""
        if expression is None:
            yield from self.get_all_items()
        elif isinstance(expression, type):
            yield from (e for e in self.get_all_items() if isinstance(e, expression))
        else:
            yield from (e for e in self.get_all_items() if expression(e))

            return list(filter(expression, self.get_all_items()))

    def reparent(self, item, parent):
        """A more fancy version of the reparent method."""
        old_parent = self.get_parent(item)

        if old_parent:
            super().reparent(item, None)
            m = self.get_matrix_i2c(old_parent)
            item.matrix.set(*item.matrix.multiply(m))
            self.request_update(old_parent)

        if parent:
            super().reparent(item, parent)
            m = self.get_matrix_i2c(parent).inverse()
            item.matrix.set(*item.matrix.multiply(m))
            self.request_update(parent)


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
        self.canvas = DiagramCanvas(self)

    @property
    def styleSheet(self) -> Optional[StyleSheet]:
        model = self.model
        style_sheet = next(model.select(StyleSheet), None)
        if not style_sheet:
            style_sheet = self.model.create(StyleSheet)
            style_sheet.styleSheet = DEFAULT_STYLE_SHEET
        return style_sheet

    def style(self, node: StyleNode) -> Style:
        style_sheet = self.styleSheet
        return {
            **FALLBACK_STYLE,  # type: ignore[misc]
            **style_sheet.match(node),
        }

    def save(self, save_func):
        """Apply the supplied save function to this diagram and the canvas."""

        super().save(save_func)
        save_func("canvas", self.canvas)

    def postload(self):
        """Handle post-load functionality for the diagram canvas."""
        super().postload()
        self.canvas.postload()

    def create(self, type, parent=None, subject=None):
        """Create a new canvas item on the canvas.

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
        item = type(connections=self.canvas.connections, id=id, model=self.model)
        assert isinstance(
            item, gaphas.Item
        ), f"Type {type} does not comply with Item protocol"
        if subject:
            item.subject = subject
        self.canvas.add(item, parent)
        self.model.handle(DiagramItemCreated(self, item))
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

    @property
    def connections(self) -> gaphas.connections.Connections:
        return self.canvas.connections

    def get_all_items(self) -> Iterable[Presentation]:
        return self.canvas.get_all_items()  # type: ignore[no-any-return]

    def get_parent(self, item: Presentation) -> Optional[Presentation]:
        return self.canvas.get_parent(item)  # type: ignore[no-any-return]

    def get_children(self, item: Presentation) -> Iterable[Presentation]:
        return self.canvas.get_children(item)  # type: ignore[no-any-return]

    def sort(self, items: Sequence[Presentation]) -> Reversible[Presentation]:
        return self.canvas.sort(items)  # type: ignore[no-any-return]

    def request_update(
        self, item: gaphas.item.Item, update: bool = True, matrix: bool = True
    ) -> None:
        self.canvas.request_update(item, update, matrix)

    def update_now(
        self,
        dirty_items: Sequence[Presentation],
        dirty_matrix_items: Sequence[Presentation],
    ) -> None:
        self.canvas.update_now(dirty_items, dirty_matrix_items)

    def register_view(self, view: gaphas.view.model.View[Presentation]) -> None:
        self.canvas.register_view(view)

    def unregister_view(self, view: gaphas.view.model.View[Presentation]) -> None:
        self.canvas.unregister_view(view)
