from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.SysML.blocks import BlockItem
from gaphor.SysML.blocks.property import PropertyItem

represents(raaml.Situation)(BlockItem)
represents(raaml.Loss)(BlockItem)
represents(raaml.Hazard)(BlockItem)
represents(raaml.ControlStructure)(BlockItem)

represents(raaml.Controller)(PropertyItem)
represents(raaml.Actuator)(PropertyItem)
represents(raaml.ControlledProcess)(PropertyItem)
