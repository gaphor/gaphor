"""The action definition for the RAAML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.i18n import i18nize
from gaphor.RAAML.fta.ftatoolbox import fta
from gaphor.RAAML.raaml import (
    FTADiagram,
    Hazard,
    Loss,
    Situation,
    STPADiagram,
    TopEvent,
)
from gaphor.RAAML.stpa.stpatoolbox import stpa
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.uml import Diagram, Package

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    fta,
    stpa,
)

raaml_diagram_types: DiagramTypes = (
    DiagramType(FTADiagram, i18nize("FTA Diagram"), (fta,)),
    DiagramType(STPADiagram, i18nize("STPA Diagram"), (stpa,)),
    DiagramType(Diagram, i18nize("Generic Diagram"), ()),
)

raaml_element_types = (
    ElementCreateInfo("package", i18nize("Package"), Package, (Package,)),
    ElementCreateInfo("topevent", i18nize("Top Event"), TopEvent, (Package,)),
    ElementCreateInfo("loss", i18nize("Loss"), Loss, (Package,)),
    ElementCreateInfo("hazard", i18nize("Hazard"), Hazard, (Package,)),
    ElementCreateInfo("situation", i18nize("Situation"), Situation, (Package,)),
)
