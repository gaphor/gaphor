from gaphor import UML
from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.deployments.artifact import ArtifactItem
from gaphor.UML.deployments.node import NodeItem


@Group.register(NodeItem, NodeItem)
class NodeGroup(AbstractGroup):
    """Add node to another node."""

    def group(self):
        self.parent.subject.nestedNode = self.item.subject

    def ungroup(self):
        del self.parent.subject.nestedNode[self.item.subject]


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
