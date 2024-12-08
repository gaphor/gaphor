"""The UML Modeling Language module is the entrypoint for UML related
assets."""

from collections.abc import Iterable

from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.UML import diagramitems, uml
from gaphor.UML.toolbox import uml_diagram_types, uml_element_types, uml_toolbox_actions
from gaphor.UML.treemodel import TreeModel


class UMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("UML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return uml_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        """Return an iterator (id, name) for each diagram type."""
        yield from uml_diagram_types

    @property
    def element_types(self) -> Iterable[ElementCreateInfo]:
        yield from uml_element_types

    @property
    def model_browser_model(self) -> type[TreeModel]:
        return TreeModel

    def lookup_element(self, name, ns=None):
        assert ns in ("UML", None)
        return getattr(uml, name, None) or getattr(diagramitems, name, None)
