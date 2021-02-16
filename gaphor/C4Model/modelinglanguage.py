"""C4 Model Language entrypoint."""

import gaphor.C4Model.grouping  # noqa
import gaphor.C4Model.iconname  # noqa
import gaphor.C4Model.propertypages  # noqa
from gaphor.abc import ModelingLanguage
from gaphor.C4Model import c4model, diagramitems
from gaphor.C4Model.toolbox import c4model_toolbox_actions
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolboxDefinition


class C4ModelLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("C4 model")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return c4model_toolbox_actions  # type: ignore[no-any-return]

    def lookup_element(self, name):
        return getattr(c4model, name, None)

    def lookup_diagram_item(self, name):
        return getattr(diagramitems, name, None)
