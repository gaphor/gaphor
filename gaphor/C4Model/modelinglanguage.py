"""C4 Model Language entrypoint."""

from typing import Iterable

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


class C4ModelLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("C4 Model")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return c4model_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        yield from c4model_diagram_types

    @property
    def element_types(self) -> Iterable[ElementCreateInfo]:
        yield from c4model_element_types

    def lookup_element(self, name):
        return getattr(c4model, name, None) or getattr(diagramitems, name, None)
