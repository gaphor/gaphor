"""The SysML Modeling Language module is the entrypoint for SysML related
assets."""

import gaphor.SysML.propertypages  # noqa
from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.SysML import diagramitems, sysml
from gaphor.SysML.toolbox import sysml_toolbox_actions


class SysMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("SysML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return sysml_toolbox_actions

    def lookup_element(self, name):
        element_type = getattr(sysml, name, None)
        if not element_type:
            element_type = getattr(diagramitems, name, None)
        return element_type
