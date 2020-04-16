"""
The UML Model Provider is the entrypoint for an application to
UML related assets.
"""

import gaphor.UML.diagramitems as diagramitems
import gaphor.UML.uml as uml
from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.SysML.toolbox import sysml_toolbox_actions


class SysMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("SysML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return sysml_toolbox_actions

    def lookup_element(self, name):
        return getattr(uml, name, None)

    def lookup_diagram_item(self, name):
        return getattr(diagramitems, name, None)
