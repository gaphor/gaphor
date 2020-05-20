from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Block
from gaphor.UML.classes import ClassItem


@represents(Block)
class BlockItem(ClassItem):
    def additional_stereotypes(self):
        return ["block"]
