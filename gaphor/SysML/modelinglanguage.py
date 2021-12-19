"""The SysML Modeling Language module is the entrypoint for SysML related
assets."""

from typing import Iterable

import gaphor.SysML.propertypages  # noqa
from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import DiagramType, ToolboxDefinition
from gaphor.SysML import diagramitems, sysml
from gaphor.SysML.toolbox import sysml_diagram_types, sysml_toolbox_actions


class SysMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("SysML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return sysml_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        yield from sysml_diagram_types

    def lookup_element(self, name):
        element_type = getattr(sysml, name, None)
        if not element_type:
            element_type = getattr(diagramitems, name, None)
        return element_type
