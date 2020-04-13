"""
The UML Model Provider is the entrypoint for an application to
UML related assets.
"""

from typing import Optional

import gaphor.UML.diagramitems as diagramitems
import gaphor.UML.uml as uml
from gaphor.abc import ModelProvider, Service
from gaphor.core import gettext
from gaphor.core.modeling import Element
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.UML.toolbox import uml_toolbox_actions


class UMLModelProvider(Service, ModelProvider):
    def __init__(self):
        pass

    def shutdown(self):
        pass

    @property
    def name(self):
        return gettext("UML")

    def lookup_element(self, name):
        return getattr(uml, name, None)

    def lookup_diagram_item(self, name):
        return getattr(diagramitems, name, None)

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return uml_toolbox_actions
