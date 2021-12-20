"""C4 Model Language entrypoint."""

from typing import Iterable

import gaphor.C4Model.grouping  # noqa
import gaphor.C4Model.iconname  # noqa
import gaphor.C4Model.propertypages  # noqa
from gaphor.abc import ModelingLanguage
from gaphor.C4Model import c4model, diagramitems
from gaphor.C4Model.toolbox import c4model_diagram_types, c4model_toolbox_actions
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import DiagramType, ToolboxDefinition


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

    def lookup_element(self, name):
        element_type = getattr(c4model, name, None)
        if not element_type:
            element_type = getattr(diagramitems, name, None)
        return element_type
