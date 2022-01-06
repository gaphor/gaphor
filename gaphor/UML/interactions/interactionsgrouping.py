from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.interactions.message import MessageItem


@Group.register(InteractionItem, LifelineItem)
class InteractionLifelineGroup(AbstractGroup):
    """Add lifeline to interaction."""

    def group(self):
        assert self.parent.diagram
        self.parent.subject.lifeline = self.item.subject
        self.item.change_parent(self.parent)

    def ungroup(self):
        """Lifelines are not ungrouped on purpose.

        They would be dangling without an owner.
        """


@Group.register(InteractionItem, MessageItem)
class InteractionMessageGroup(AbstractGroup):
    """Add message to interaction."""

    def group(self):
        if not self.item.subject:
            return
        assert self.parent.diagram
        self.parent.subject.message = self.item.subject
        self.item.change_parent(self.parent)

    def ungroup(self):
        """Messages are not ungrouped on purpose.

        They would be dangling without an owner.
        """
