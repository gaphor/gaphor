from gaphor import UML
from gaphor.diagram.group import group
from gaphor.UML.uml import Artifact, Node


@group.register(Node, Node)
def node_group(parent, element):
    parent.nestedNode = element
    return True


@group.register(Node, Artifact)
def node_artifact_group(node, artifact):
    """Deploy artifact on node."""
    # deploy artifact on node
    # TODO: remove existing deployment, if any
    deployment = node.model.create(UML.Deployment)
    node.deployment = deployment
    deployment.deployedArtifact = artifact
    return True


def ungroup(node, artifact):
    for deployment in node.deployment:
        if deployment.deployedArtifact[0] is artifact:
            deployment.unlink()
