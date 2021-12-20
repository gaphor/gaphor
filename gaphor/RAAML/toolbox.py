"""The action definition for the RAAML toolbox."""
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ToolboxDefinition,
    general_tools,
)
from gaphor.i18n import gettext
from gaphor.RAAML.fta.ftatoolbox import fta
from gaphor.RAAML.stpa.stpatoolbox import stpa

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    fta,
    stpa,
)

raaml_diagram_types: DiagramTypes = (
    DiagramType("fta", gettext("New FTA Diagram"), (fta,)),
    DiagramType("stpa", gettext("New STPA Diagram"), (stpa,)),
)
