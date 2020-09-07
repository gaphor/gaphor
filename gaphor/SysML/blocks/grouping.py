from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.property import PropertyItem


@Group.register(BlockItem, PropertyItem)
class PropertyGroup(AbstractGroup):
    """Add Property to a Block."""

    def can_contain(self) -> bool:
        return (
            not self.item.subject.association
            or self.item.subject.owner is self.parent.subject
        )

    def group(self):
        if not self.item.subject.association:
            self.parent.subject.ownedAttribute = self.item.subject

    def ungroup(self):
        if not self.item.subject.association:
            del self.parent.subject.ownedAttribute[self.item.subject]
