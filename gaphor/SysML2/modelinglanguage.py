"""Systems Modeling Language version 2."""

import os
from collections.abc import Iterable

from gaphor.abc import ModelingLanguage
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.i18n import i18nize
from gaphor.KerML import kerml
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
        yield ElementCreateInfo(
            "package",
            i18nize("Package"),
            kerml.Package,
            (kerml.Package,),
        )
        yield ElementCreateInfo(
            "part-definition",
            i18nize("Part Definition"),
            sysml2.PartDefinition,
            (kerml.Package,),
        )
        yield ElementCreateInfo(
            "requirement-definition",
            i18nize("Requirement Definition"),
            sysml2.RequirementDefinition,
            (kerml.Package,),
        )

    @property
    def model_browser_model(self):
        from gaphor.SysML2.treemodel import TreeModel

        return TreeModel

    def lookup_element(self, name, ns=None):
        if ns == "SysML2":
            return getattr(sysml2, name, None)
        return None
