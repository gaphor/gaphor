"""The SysML Modeling Language module is the entrypoint for SysML related
assets."""

from typing import Iterable

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
        return getattr(sysml, name, None) or getattr(diagramitems, name, None)

    def format_diagram_label(self, diagram) -> str:
        return str(diagram.name)
