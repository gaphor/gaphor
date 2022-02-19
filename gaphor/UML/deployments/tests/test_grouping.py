from gaphor import UML
from gaphor.UML.deployments import ArtifactItem, NodeItem


class TestNodesGroup:
    """Nodes grouping tests."""

    def test_grouping(self, case):
        """Test node within another node composition."""
        n1 = case.create(NodeItem, UML.Node)
        n2 = case.create(NodeItem, UML.Node)

        case.group(n1, n2)

        assert n2.subject in n1.subject.nestedNode
        assert n1.subject not in n2.subject.nestedNode

    def test_ungrouping(self, case):
        """Test decomposition of component from node."""
        n1 = case.create(NodeItem, UML.Node)
        n2 = case.create(NodeItem, UML.Node)

        case.group(n1, n2)
        case.ungroup(n1, n2)

        assert n2.subject not in n1.subject.nestedNode
        assert n1.subject not in n2.subject.nestedNode


class TestNodeArtifactGroup:
    def test_grouping(self, case):
        """Test artifact within node deployment."""
        n = case.create(NodeItem, UML.Node)
        a = case.create(ArtifactItem, UML.Artifact)

        case.group(n, a)

        assert len(n.subject.deployment) == 1
        assert n.subject.deployment[0].deployedArtifact[0] is a.subject

    def test_ungrouping(self, case):
        """Test removal of artifact from node."""
        n = case.create(NodeItem, UML.Node)
        a = case.create(ArtifactItem, UML.Artifact)

        case.group(n, a)
        case.ungroup(n, a)

        assert len(n.subject.deployment) == 0
        assert len(case.kindof(UML.Deployment)) == 0
