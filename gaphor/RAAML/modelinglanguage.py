"""The RAAML Modeling Language module is the entrypoint for RAAML related
assets."""

import gaphor.SysML.propertypages  # noqa
from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.RAAML import diagramitems, raaml
from gaphor.RAAML.toolbox import raaml_toolbox_actions


class RAAMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("RAAML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return raaml_toolbox_actions

    def lookup_element(self, name):
        element_type = getattr(raaml, name, None)
        if not element_type:
            element_type = getattr(diagramitems, name, None)
        return element_type
