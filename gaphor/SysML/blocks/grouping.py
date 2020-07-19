from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.property import PropertyItem


@Group.register(BlockItem, PropertyItem)
class NodeGroup(AbstractGroup):
    """
    Add node to another node.
    """

    def group(self):
        self.parent.subject.ownedAttribute = self.item.subject

    def ungroup(self):
        del self.parent.subject.ownedAttribute[self.item.subject]
