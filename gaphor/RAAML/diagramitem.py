from gaphor.diagram.support import represents
from gaphor.RAAML.raaml import FTADiagram, STPADiagram
from gaphor.UML.general.diagramitem import DiagramItem

represents(FTADiagram)(DiagramItem)
represents(STPADiagram)(DiagramItem)
