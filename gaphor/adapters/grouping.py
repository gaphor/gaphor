from zope import interface, component

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.diagram import DiagramItemMeta
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

    element_factory = inject('element_factory')

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



class NodeComponentGroup(AbstractGroup):
    """
    Add components to another node using internal structures.
    """
    def pre_can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and issubclass(self.item, items.ComponentItem)

    def can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and isinstance(self.item, items.ComponentItem)

    def group(self):
        node = self.parent.subject
        component = self.item.subject

        # node attribute
        a1 = self.element_factory.create(UML.Property)
        a1.aggregation = 'composite'
        # component attribute
        a2 = self.element_factory.create(UML.Property)

        e1 = self.element_factory.create(UML.ConnectorEnd)
        e2 = self.element_factory.create(UML.ConnectorEnd)

        # create connection between node and component
        e1.role = a1
        e2.role = a2
        connector = self.element_factory.create(UML.Connector)
        connector.end = e1
        connector.end = e2

        # compose component within node
        node.ownedAttribute = a1
        node.ownedConnector = connector
        component.ownedAttribute =  a2


    def ungroup(self):
        node = self.parent.subject
        component = self.item.subject
        for connector in node.ownedConnector:
            e1 = connector.end[0]
            e2 = connector.end[1]
            if e1.role in node.ownedAttribute and e2.role in component.ownedAttribute:
                e1.role.unlink()
                e2.role.unlink()
                e1.unlink()
                e2.unlink()
                connector.unlink()
                log.debug('Removed %s from node %s' % (self.item.subject, node))


component.provideAdapter(factory=NodeComponentGroup,
        adapts=(items.NodeItem, DiagramItemMeta))
component.provideAdapter(factory=NodeComponentGroup,
        adapts=(items.NodeItem, items.ComponentItem))

