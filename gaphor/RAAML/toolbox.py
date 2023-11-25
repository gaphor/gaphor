"""The action definition for the RAAML toolbox."""
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
    general_tools,
)
from gaphor.i18n import i18nize
from gaphor.RAAML.fta.ftatoolbox import fta
from gaphor.RAAML.raaml import Hazard, Loss, Situation, TopEvent
from gaphor.RAAML.stpa.stpatoolbox import stpa
from gaphor.UML.uml import Package

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    fta,
    stpa,
)

raaml_diagram_types: DiagramTypes = (
    DiagramType("fta", i18nize("New FTA Diagram"), (fta,)),
    DiagramType("stpa", i18nize("New STPA Diagram"), (stpa,)),
)

raaml_element_types = (
    ElementCreateInfo("topevent", i18nize("New Top Event"), TopEvent, (Package,)),
    ElementCreateInfo("loss", i18nize("New Loss"), Loss, (Package,)),
    ElementCreateInfo("hazard", i18nize("New Hazard"), Hazard, (Package,)),
    ElementCreateInfo("situation", i18nize("New Situation"), Situation, (Package,)),
)
