from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.UML.deployments import ArtifactItem, NodeItem


class TestNodesGroup:
    """Nodes grouping tests."""

    def test_grouping(self, case):
        """Test node within another node composition."""
        n1 = case.create(NodeItem, UML.Node)
        n2 = case.create(NodeItem, UML.Node)

        assert group(n1.subject, n2.subject)

        assert n2.subject in n1.subject.nestedNode
        assert n1.subject not in n2.subject.nestedNode

    def test_ungrouping(self, case):
        """Test decomposition of component from node."""
        n1 = case.create(NodeItem, UML.Node)
        n2 = case.create(NodeItem, UML.Node)

        assert group(n1.subject, n2.subject)
        assert ungroup(n1.subject, n2.subject)

        assert n2.subject not in n1.subject.nestedNode
        assert n1.subject not in n2.subject.nestedNode


class TestNodeArtifactGroup:
    def test_grouping(self, case):
        """Test artifact within node deployment."""
        n = case.create(NodeItem, UML.Node)
        a = case.create(ArtifactItem, UML.Artifact)

        assert group(n.subject, a.subject)

        assert len(n.subject.deployment) == 1
        assert n.subject.deployment[0].deployedArtifact[0] is a.subject

    def test_ungrouping(self, case):
        """Test removal of artifact from node."""
        n = case.create(NodeItem, UML.Node)
        a = case.create(ArtifactItem, UML.Artifact)

        assert group(n.subject, a.subject)
        assert ungroup(n.subject, a.subject)

        assert len(n.subject.deployment) == 0
        assert len(case.kindof(UML.Deployment)) == 0
