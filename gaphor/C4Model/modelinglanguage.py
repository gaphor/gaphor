"""C4 Model Language entrypoint."""

from collections.abc import Iterable

from gaphor.abc import ModelingLanguage
from gaphor.C4Model import c4model, diagramitems
from gaphor.C4Model.toolbox import (
    c4model_diagram_types,
    c4model_element_types,
    c4model_toolbox_actions,
)
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.diagram.support import represents
from gaphor.UML.general.diagramitem import DiagramItem
from gaphor.UML.treemodel import TreeModel

represents(c4model.C4Diagram)(DiagramItem)


class C4ModelLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("C4")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return c4model_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        yield from c4model_diagram_types

    @property
    def element_types(self) -> Iterable[ElementCreateInfo]:
        yield from c4model_element_types

    @property
    def model_browser_model(self) -> type[TreeModel]:
        return TreeModel

    def lookup_element(self, name, ns=None):
        assert ns in ("C4Model", None)
        return getattr(c4model, name, None) or getattr(diagramitems, name, None)
