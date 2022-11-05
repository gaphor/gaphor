from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.SysML.blocks import BlockItem

represents(raaml.Situation)(BlockItem)
represents(raaml.Loss)(BlockItem)
represents(raaml.Hazard)(BlockItem)
represents(raaml.ControlStructure)(BlockItem)
