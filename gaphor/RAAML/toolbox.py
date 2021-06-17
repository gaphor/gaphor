"""The action definition for the RAAML toolbox."""
from gaphor.diagram.diagramtoolbox import ToolboxDefinition, general_tools
from gaphor.RAAML.fta.ftatoolbox import fta
from gaphor.RAAML.stpa.stpatoolbox import stpa

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    fta,
    stpa,
)
