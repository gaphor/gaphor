from gaphor import UML
from gaphor.diagram.grouping import Group, AbstractGroup
from gaphor.diagram.components.node import NodeItem
from gaphor.diagram.components.component import ComponentItem
from gaphor.diagram.components.artifact import ArtifactItem
from gaphor.diagram.usecases import UseCaseItem


@Group.register(NodeItem, NodeItem)
class NodeGroup(AbstractGroup):
    """
    Add node to another node.
    """

    def group(self):
        self.parent.subject.nestedNode = self.item.subject

    def ungroup(self):
        del self.parent.subject.nestedNode[self.item.subject]


@Group.register(NodeItem, ComponentItem)
class NodeComponentGroup(AbstractGroup):
    """
    Add components to node using internal structures.
    """

    def group(self):
        node = self.parent.subject
        component = self.item.subject

        # node attribute
        a1 = node.model.create(UML.Property)
        a1.aggregation = "composite"
        # component attribute
        a2 = node.model.create(UML.Property)

        e1 = node.model.create(UML.ConnectorEnd)
        e2 = node.model.create(UML.ConnectorEnd)

        # create connection between node and component
        e1.role = a1
        e2.role = a2
        connector = node.model.create(UML.Connector)
        connector.end = e1
        connector.end = e2

        # compose component within node
        node.ownedAttribute = a1
        node.ownedConnector = connector
        component.ownedAttribute = a2

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


@Group.register(NodeItem, ArtifactItem)
class NodeArtifactGroup(AbstractGroup):
    """
    Deploy artifact on node.
    """

    def group(self):
        node = self.parent.subject
        artifact = self.item.subject

        # deploy artifact on node
        deployment = node.model.create(UML.Deployment)
        node.deployment = deployment
        deployment.deployedArtifact = artifact

    def ungroup(self):
        node = self.parent.subject
        artifact = self.item.subject
        for deployment in node.deployment:
            if deployment.deployedArtifact[0] is artifact:
                deployment.unlink()


@Group.register(ComponentItem, UseCaseItem)
class SubsystemUseCaseGroup(AbstractGroup):
    """
    Make subsystem a subject of an use case.
    """

    def group(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject = component

    def ungroup(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject.remove(component)
