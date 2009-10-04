from zope import interface, component

from gaphor.diagram import items
from gaphor.diagram.interfaces import IGroup

class AbstractGroup(object):
    """
    Base class for grouping UML objects.

    :Attributes:
     parent
        Parent item, which groups other items.
     item
        Item to be groupped.
    """
    interface.implements(IGroup)

    def __init__(self, parent, item):
        self.parent = parent
        self.item = item


    def pre_can_contain(self):
        raise NotImplemented, 'This is abstract method'


    def can_contain(self):
        raise NotImplemented, 'This is abstract method'


    def group(self):
        raise NotImplemented, 'This is abstract method'


    def ungroup(self):
        raise NotImplemented, 'This is abstract method'



from gaphor.diagram import DiagramItemMeta
class InteractionLifelineGroup(AbstractGroup):
    """
    Add lifeline to interaction.
    """

    def pre_can_contain(self):
        return isinstance(self.parent, items.InteractionItem) \
                and issubclass(self.item, items.LifelineItem)


    def can_contain(self):
        return isinstance(self.parent, items.InteractionItem) \
                and isinstance(self.item, items.LifelineItem)


    def group(self):
        self.parent.subject.lifeline = self.item.subject
        self.parent.canvas.reparent(self.item, self.parent)


    def ungroup(self):
        del self.parent.subject.lifeline[self.item.subject]


component.provideAdapter(factory=InteractionLifelineGroup,
        adapts=(items.InteractionItem, DiagramItemMeta))
component.provideAdapter(factory=InteractionLifelineGroup,
        adapts=(items.InteractionItem, items.LifelineItem))



class NodeGroup(AbstractGroup):
    """
    Add node to another node.
    """
    def pre_can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and issubclass(self.item, items.NodeItem)

    def can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and isinstance(self.item, items.NodeItem)

    def group(self):
        self.parent.subject.nestedNode = self.item.subject
        self.parent.canvas.reparent(self.item, self.parent)


    def ungroup(self):
        del self.parent.subject.nestedNode[self.item.subject]


component.provideAdapter(factory=NodeGroup,
        adapts=(items.NodeItem, DiagramItemMeta))
component.provideAdapter(factory=NodeGroup,
        adapts=(items.NodeItem, items.NodeItem))
