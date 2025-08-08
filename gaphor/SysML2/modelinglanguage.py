"""Systems Modeling Language version 2."""

import os
from collections.abc import Iterable

from gaphor.abc import ModelingLanguage
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.SysML2 import sysml2
from gaphor.SysML2.toolbox import sysml2_toolbox_actions


class SysML2ModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return "SysML 2.0" if os.getenv("GAPHOR_SYSML2") else ""

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return sysml2_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        yield from ()

    @property
    def element_types(self) -> Iterable[ElementCreateInfo]:
        yield from ()

    @property
    def model_browser_model(self):
        # Use UML tree model for the time being
        from gaphor.UML.treemodel import TreeModel

        return TreeModel

    def lookup_element(self, name, ns=None):
        if ns == "SysML2":
            return getattr(sysml2, name, None)
        return None
