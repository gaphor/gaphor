from gaphor import UML
from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.components.artifact import ArtifactItem
from gaphor.UML.components.component import ComponentItem
from gaphor.UML.components.node import NodeItem
from gaphor.UML.usecases import UseCaseItem


@Group.register(NodeItem, NodeItem)
class NodeGroup(AbstractGroup):
    """Add node to another node."""

    def group(self):
        self.parent.subject.nestedNode = self.item.subject

    def ungroup(self):
        del self.parent.subject.nestedNode[self.item.subject]


@Group.register(NodeItem, ComponentItem)
class NodeComponentGroup(AbstractGroup):
    """Add components to node using internal structures."""

    def group(self):
        node = self.parent.subject
        component = self.item.subject

        # attributes
        node_attr = node.model.create(UML.Property)
        node_attr.aggregation = "composite"
        comp_attr = node.model.create(UML.Property)

        node_end = node.model.create(UML.ConnectorEnd)
        comp_end = node.model.create(UML.ConnectorEnd)

        # create connection between node and component
        node_end.role = node_attr
        comp_end.role = comp_attr

        connector = node.model.create(UML.Connector)
        connector.end = node_end
        connector.end = comp_end

        # compose component within node
        node.ownedAttribute = node_attr
        node.ownedConnector = connector
        component.ownedAttribute = comp_attr

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
    """Deploy artifact on node."""

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
    """Make subsystem a subject of an use case."""

    def group(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject = component

    def ungroup(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject.remove(component)
