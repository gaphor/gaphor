"""
Grouping functionality allows to nest one item within another item (parent
item). This is useful in several use cases

- artifact deployed within a node
- a class within a package or a component
- composite structures (i.e. component within a node)

The grouping adapters has to implement three methods, see `AbstractGroup`
class.

It is important to note, that grouping adapters can be queried before
instance of an item to be grouped is created. This happens when item
is about to be created. Therefore `AbstractGroup.can_contain` has
to be aware that `AbstractGroup.item` can be null.
"""

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
        Item to be grouped.
     item_class
        Class of item to be grouped.
    """
    interface.implements(IGroup)

    element_factory = inject('element_factory')

    def __init__(self, parent, item):
        self.parent = parent
        self.item = item
        self.item_class = type(self.item)

        if isinstance(item, DiagramItemMeta):
            self.item_class = item
            self.item = None


    def can_contain(self):
        """
        Check if parent can contain an item.
        """
        raise NotImplemented, 'This is abstract method'


    def group(self):
        """
        Group an item within parent.
        """
        raise NotImplemented, 'This is abstract method'


    def ungroup(self):
        """
        Remove item from parent.
        """
        raise NotImplemented, 'This is abstract method'



class InteractionLifelineGroup(AbstractGroup):
    """
    Add lifeline to interaction.
    """
    def can_contain(self):
        return isinstance(self.parent, items.InteractionItem) \
            and issubclass(self.item_class, items.LifelineItem)


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
    def can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and issubclass(self.item_class, items.NodeItem)


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
    Add components to node using internal structures.
    """
    def can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and issubclass(self.item_class, items.ComponentItem)


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
                log.debug('Removed %s from node %s' % (component, node))


component.provideAdapter(factory=NodeComponentGroup,
        adapts=(items.NodeItem, DiagramItemMeta))
component.provideAdapter(factory=NodeComponentGroup,
        adapts=(items.NodeItem, items.ComponentItem))



class NodeArtifactGroup(AbstractGroup):
    """
    Deploy artifact on node.
    """
    def can_contain(self):
        return isinstance(self.parent, items.NodeItem) \
                and issubclass(self.item_class, items.ArtifactItem)


    def group(self):
        node = self.parent.subject
        artifact = self.item.subject

        # deploy artifact on node
        deployment = self.element_factory.create(UML.Deployment)
        node.deployment = deployment
        deployment.deployedArtifact = artifact


    def ungroup(self):
        node = self.parent.subject
        artifact = self.item.subject
        for deployment in node.deployment:
            if deployment.deployedArtifact[0] is artifact:
                deployment.unlink()
                log.debug('Removed %s from node %s' % (artifact, node))


component.provideAdapter(factory=NodeArtifactGroup,
        adapts=(items.NodeItem, DiagramItemMeta))
component.provideAdapter(factory=NodeArtifactGroup,
        adapts=(items.NodeItem, items.ArtifactItem))



class SubsystemUseCaseGroup(AbstractGroup):
    """
    Make subsystem a subject of an use case.
    """
    def can_contain(self):
        return isinstance(self.parent, items.SubsystemItem) \
                and issubclass(self.item_class, items.UseCaseItem)


    def group(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject = component


    def ungroup(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject.remove(component)


component.provideAdapter(factory=SubsystemUseCaseGroup,
        adapts=(items.SubsystemItem, DiagramItemMeta))
component.provideAdapter(factory=SubsystemUseCaseGroup,
        adapts=(items.SubsystemItem, items.UseCaseItem))



class ActivityPartitionsGroup(AbstractGroup):
    """
    Group activity partitions.
    """
    def can_contain(self):
        return isinstance(self.parent, items.PartitionItem) \
                and issubclass(self.item_class, items.PartitionItem) \
                and self.parent.subject \
                and len(self.parent.subject.node) == 0


    def group(self):
        partition = self.parent.subject
        subpartition = self.item.subject
        partition.subpartition = subpartition
        self.parent.request_update()
        self.item.request_update()


    def ungroup(self):
        partition = self.parent.subject
        subpartition = self.item.subject
        partition.subpartition.remove(subpartition)
        self.parent.request_update()
        self.item.request_update()


component.provideAdapter(factory=ActivityPartitionsGroup,
        adapts=(items.PartitionItem, DiagramItemMeta))
component.provideAdapter(factory=ActivityPartitionsGroup,
        adapts=(items.PartitionItem, items.PartitionItem))



class ActivityNodePartitionGroup(AbstractGroup):
    """
    Group activity nodes within activity partition.
    """
    def can_contain(self):
        return isinstance(self.parent, items.PartitionItem) \
                and issubclass(self.item_class, (items.ActivityNodeItem,
                    items.ActionItem,
                    items.ObjectNodeItem)) \
                and self.parent.subject \
                and len(self.parent.subject.subpartition) == 0


    def group(self):
        partition = self.parent.subject
        node = self.item.subject
        partition.node = node
        self.parent.request_update()
        self.item.request_update()


    def ungroup(self):
        partition = self.parent.subject
        node = self.item.subject
        partition.node.remove(node)
        self.parent.request_update()
        self.item.request_update()


component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, DiagramItemMeta))
component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ActivityNodeItem))
component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ActionItem))
component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ObjectNodeItem))

