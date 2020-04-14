"""
The UML Model Provider is the entrypoint for an application to
UML related assets.
"""

import gaphor.UML.diagramitems as diagramitems
import gaphor.UML.uml as uml
from gaphor.abc import ModelProvider
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.SysML.toolbox import sysml_toolbox_actions


class SysMLModelProvider(ModelProvider):
    @property
    def name(self) -> str:
        return gettext("SysML")

    def lookup_element(self, name):
        return getattr(uml, name, None)

    def lookup_diagram_item(self, name):
        return getattr(diagramitems, name, None)

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return sysml_toolbox_actions
