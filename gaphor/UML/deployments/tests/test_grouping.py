from gaphor import UML
from gaphor.diagram.group import group, ungroup


def test_node_group(element_factory):
    """Test node within another node composition."""
    n1 = element_factory.create(UML.Node)
    n2 = element_factory.create(UML.Node)

    assert group(n1, n2)

    assert n2 in n1.nestedNode
    assert n1 not in n2.nestedNode


def test_node_ungroup(element_factory):
    """Test decomposition of component from node."""
    n1 = element_factory.create(UML.Node)
    n2 = element_factory.create(UML.Node)

    assert group(n1, n2)
    assert ungroup(n1, n2)

    assert n2 not in n1.nestedNode
    assert n1 not in n2.nestedNode


def test_node_ungroup_wrong_parent(element_factory):
    """Test decomposition of component from node."""
    n1 = element_factory.create(UML.Node)
    n2 = element_factory.create(UML.Node)
    wrong = element_factory.create(UML.Node)

    assert group(n1, n2)
    assert not ungroup(wrong, n2)

    assert n2 in n1.nestedNode
    assert n1 not in n2.nestedNode


def test_artifact_group(element_factory):
    """Test artifact within node deployment."""
    n = element_factory.create(UML.Node)
    a = element_factory.create(UML.Artifact)

    assert group(n, a)

    assert n.deployment
    assert n.deployment[0].deployedArtifact[0] is a
    assert len(element_factory.lselect(UML.Deployment)) == 1


def test_artifact_group_is_idempotent(element_factory):
    """Test artifact within node deployment."""
    n = element_factory.create(UML.Node)
    a = element_factory.create(UML.Artifact)

    assert group(n, a)
    assert group(n, a)
    assert group(n, a)

    assert n.deployment
    assert n.deployment[0].deployedArtifact[0] is a
    assert len(element_factory.lselect(UML.Deployment)) == 1


def test_artifact_ungroup(element_factory):
    """Test removal of artifact from node."""
    n = element_factory.create(UML.Node)
    a = element_factory.create(UML.Artifact)

    assert group(n, a)
    assert ungroup(n, a)

    assert not n.deployment
    assert not element_factory.lselect(UML.Deployment)


def test_artifact_ungroup_wrong_parent(element_factory):
    """Test removal of artifact from node."""
    n = element_factory.create(UML.Node)
    a = element_factory.create(UML.Artifact)
    wrong = element_factory.create(UML.Node)

    assert group(n, a)
    assert not ungroup(wrong, a)

    assert n.deployment
    assert element_factory.lselect(UML.Deployment)
