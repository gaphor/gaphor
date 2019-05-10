from ..grouping import Group, AbstractGroup
from .interaction import InteractionItem
from .lifeline import LifelineItem


@Group.register(InteractionItem, LifelineItem)
class InteractionLifelineGroup(AbstractGroup):
    """
    Add lifeline to interaction.
    """

    def group(self):
        self.parent.subject.lifeline = self.item.subject
        self.parent.canvas.reparent(self.item, self.parent)

    def ungroup(self):
        del self.parent.subject.lifeline[self.item.subject]
