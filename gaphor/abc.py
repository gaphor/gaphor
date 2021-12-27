from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from gaphor.core.modeling import Element
    from gaphor.diagram.diagramtoolbox import DiagramType, ToolboxDefinition


class Service(metaclass=ABCMeta):
    """Base interface for all services in Gaphor."""

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the services, free resources."""


class ActionProvider(metaclass=ABCMeta):
    """An action provider is a special service that provides actions (see
    gaphor/action.py)."""


class ModelingLanguage(metaclass=ABCMeta):
    """A model provider is a special service that provides an entrypoint to a
    model implementation, such as UML, SysML, RAAML."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human readable name of the model."""

    @property
    @abstractmethod
    def toolbox_definition(self) -> ToolboxDefinition:
        """Get structure for the toolbox."""

    @property
    @abstractmethod
    def diagram_types(self) -> Iterable[DiagramType]:
        """Iterate diagram types."""

    @abstractmethod
    def lookup_element(self, name: str) -> type[Element] | None:
        """Look up a model element type (class) by name."""
