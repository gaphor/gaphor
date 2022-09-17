from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.UML.uml import Artifact, Node


@group.register(Node, Node)
def node_group(parent, element):
    parent.nestedNode = element
    return True


@ungroup.register(Node, Node)
def node_ungroup(parent, element):
    if element.node is parent:
        del element.node
        return True
    return False


@group.register(Node, Artifact)
def node_artifact_group(node, artifact):
    deployments = set(node.deployment) & set(artifact.deployment)
    if not deployments:
        deployment = node.model.create(UML.Deployment)
        node.deployment = deployment
        deployment.deployedArtifact = artifact
    return True


@ungroup.register(Node, Artifact)
def node_artifact_ungroup(node, artifact):
    if deployments := set(node.deployment) & set(artifact.deployment):
        for deployment in deployments:
            deployment.unlink()
        return True
    return False
