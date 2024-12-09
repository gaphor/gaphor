from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from gi.repository import Gio

    from gaphor.core.modeling import Base
    from gaphor.diagram.diagramtoolbox import (
        DiagramType,
        ElementCreateInfo,
        ToolboxDefinition,
    )


class Service(abc.ABC):
    """Base interface for all services in Gaphor."""

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Shutdown the services, free resources."""


class ActionProvider:
    """An action provider is a special service that provides actions via
    ``@action`` decorators on its methods (see gaphor/action.py)."""


class ModelingLanguage(abc.ABC):
    """A model provider is a special service that provides an entrypoint to a
    model implementation, such as UML, SysML, RAAML."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable name of the modeling language."""

    @property
    @abc.abstractmethod
    def toolbox_definition(self) -> ToolboxDefinition:
        """Get structure for the toolbox."""

    @property
    @abc.abstractmethod
    def diagram_types(self) -> Iterable[DiagramType]:
        """Iterate diagram types."""

    @property
    @abc.abstractmethod
    def element_types(self) -> Iterable[ElementCreateInfo]:
        """Iterate element types."""

    @property
    @abc.abstractmethod
    def model_browser_model(self) -> type[TreeModel]:
        """A model for use in the Model Browser."""

    @abc.abstractmethod
    def lookup_element(self, name: str, ns: str | None = None) -> type[Base] | None:
        """Look up a model element type by (class) name.

        A namespace may be provided. This will allow the model to be loaded from
        that specific modeling language only.
        """


class TreeItem(Protocol):
    @property
    def element(self) -> Base: ...

    @property
    def readonly_text(self) -> str: ...


T = TypeVar("T", bound=TreeItem, contravariant=True)


class TreeModel(Protocol[T]):
    def __init__(self, *args, on_select=None, on_sync=None): ...

    @property
    def root(self) -> Gio.ListStore: ...

    def child_model(self, item: T) -> Gio.ListStore | None: ...

    @property
    def template(self) -> str: ...

    def tree_item_sort(self, a, b) -> int: ...

    def should_expand(self, item: T, element: Base) -> bool: ...

    def shutdown(self) -> None: ...
