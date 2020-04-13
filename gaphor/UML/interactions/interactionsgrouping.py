from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem


@Group.register(InteractionItem, LifelineItem)
class InteractionLifelineGroup(AbstractGroup):
    """
    Add lifeline to interaction.
    """

    def group(self):
        assert self.parent.canvas
        self.parent.subject.lifeline = self.item.subject
        self.parent.canvas.reparent(self.item, self.parent)

    def ungroup(self):
        del self.parent.subject.lifeline[self.item.subject]
