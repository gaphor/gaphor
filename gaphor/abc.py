from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Type
    from gaphor.core.modeling import Element, Presentation
    from gaphor.diagram.diagramtoolbox import ToolboxDefinition


class Service(metaclass=abc.ABCMeta):
    """
    Base interface for all services in Gaphor.
    """

    @abc.abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the services, free resources.
        """


class ActionProvider(metaclass=abc.ABCMeta):
    """
    An action provider is a special service that provides actions
    (see gaphor/action.py).
    """


class ModelingLanguage(metaclass=abc.ABCMeta):
    """
    A model provider is a special service that provides an entrypoint
    to a model implementation, such as UML, SysML, Safety.
    """

    @abc.abstractproperty
    def name(self) -> str:
        """
        Human readable name of the model.
        """

    @abc.abstractproperty
    def toolbox_definition(self) -> ToolboxDefinition:
        """
        Get structure for the toolbox.
        """

    @abc.abstractmethod
    def lookup_element(self, name: str) -> Optional[Type[Element]]:
        """
        Look up a model element type (class) by name.
        """

    @abc.abstractmethod
    def lookup_diagram_item(self, name: str) -> Optional[Type[Presentation]]:
        """
        Look up a diagram item type (class) by name.
        """
