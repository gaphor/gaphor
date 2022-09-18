"""The RAAML Modeling Language module is the entrypoint for RAAML related
assets."""

from typing import Iterable

import gaphor.SysML.propertypages  # noqa
from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import DiagramType, ToolboxDefinition
from gaphor.RAAML import diagramitems, raaml
from gaphor.RAAML.toolbox import raaml_diagram_types, raaml_toolbox_actions


class RAAMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("RAAML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return raaml_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        yield from raaml_diagram_types

    def lookup_element(self, name):
        return getattr(raaml, name, None) or getattr(diagramitems, name, None)
