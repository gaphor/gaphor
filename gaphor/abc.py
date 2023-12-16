from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from gaphor.core.modeling import Element
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


class ActionProvider(abc.ABC):
    """An action provider is a special service that provides actions via
    ``@action`` decorators on its methods (see gaphor/action.py)."""

    @abc.abstractmethod
    def __init__(self):
        pass


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

    @abc.abstractmethod
    def lookup_element(self, name: str) -> type[Element] | None:
        """Look up a model element type by (class) name."""
