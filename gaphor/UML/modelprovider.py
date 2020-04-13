"""
The UML Model Provider is the entrypoint for an application to
UML related assets.
"""

from typing import Optional

import gaphor.UML.uml as uml
from gaphor.abc import ModelProvider, Service
from gaphor.core.modeling import Element
from gaphor.UML.toolbox import uml_toolbox_actions


class UMLModelProvider(Service, ModelProvider):
    def __init__(self):
        pass

    def shutdown(self):
        pass

    def lookup(self, name):
        """
        Lookup a model element class by name.
        """
        return getattr(uml, name, None)

    def toolbox_definition(self):
        return uml_toolbox_actions
