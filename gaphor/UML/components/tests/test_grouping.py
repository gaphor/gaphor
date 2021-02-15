from gaphor import UML
from gaphor.UML.components import ArtifactItem, ComponentItem, NodeItem
from gaphor.UML.usecases import UseCaseItem


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


class TestNodeComponentGroup:
    def test_grouping(self, case):
        """Test component within node composition."""
        n = case.create(NodeItem, UML.Node)
        c = case.create(ComponentItem, UML.Component)

        case.group(n, c)

        assert len(n.subject.ownedAttribute) == 1
        assert len(n.subject.ownedConnector) == 1
        assert len(c.subject.ownedAttribute) == 1
        assert len(case.kindof(UML.ConnectorEnd)) == 2

        a1 = n.subject.ownedAttribute[0]
        a2 = c.subject.ownedAttribute[0]

        assert a1.isComposite
        assert a1 in n.subject.part

        connector = n.subject.ownedConnector[0]
        assert connector.end[0].role is a1
        assert connector.end[1].role is a2

    def test_ungrouping(self, case):
        """Test decomposition of component from node."""
        n = case.create(NodeItem, UML.Node)
        c = case.create(ComponentItem, UML.Component)

        case.group(n, c)
        case.ungroup(n, c)

        assert len(n.subject.ownedAttribute) == 0
        assert len(c.subject.ownedAttribute) == 0
        assert len(case.kindof(UML.Property)) == 0
        assert len(case.kindof(UML.Connector)) == 0
        assert len(case.kindof(UML.ConnectorEnd)) == 0


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


class TestSubsystemUseCaseGroup:
    def test_grouping(self, case):
        """Test adding an use case to a subsystem."""
        s = case.create(ComponentItem, UML.Component)
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)

        case.group(s, uc1)
        assert len(uc1.subject.subject) == 1
        case.group(s, uc2)
        assert len(uc2.subject.subject) == 1

        assert len(s.subject.useCase) == 2

    def test_grouping_with_namespace(self, case):
        """Test adding an use case to a subsystem (with namespace)"""
        s = case.create(ComponentItem, UML.Component)
        uc = case.create(UseCaseItem, UML.UseCase)

        case.group(s, uc)
        assert len(uc.subject.subject) == 1
        assert s.subject in uc.subject.subject

    def test_ungrouping(self, case):
        """Test removal of use case from subsystem."""
        s = case.create(ComponentItem, UML.Component)
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)

        case.group(s, uc1)
        case.group(s, uc2)

        case.ungroup(s, uc1)
        assert len(uc1.subject.subject) == 0
        assert len(s.subject.useCase) == 1

        case.ungroup(s, uc2)
        assert len(uc2.subject.subject) == 0
        assert len(s.subject.useCase) == 0
