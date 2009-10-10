"""
Tests for grouping functionality in Gaphor.
"""

from gaphor import UML
from gaphor.ui.namespace import NamespaceModel
from gaphor.diagram import items
from gaphor.diagram.interfaces import IGroup
from zope import component

from gaphor.tests import TestCase 

class NodeComponentGroupTestCase(TestCase):
    def group(self, parent, item):
        """
        Group item within a parent.
        """
        query = (parent, item)
        adapter = component.queryMultiAdapter(query, IGroup)
        adapter.group()


    def ungroup(self, parent, item):
        """
        Remove item from a parent.
        """
        query = (parent, item)
        adapter = component.queryMultiAdapter(query, IGroup)
        adapter.ungroup()


    def test_grouping(self):
        """Test component within node composition
        """
        n = self.create(items.NodeItem, UML.Node)
        c = self.create(items.ComponentItem, UML.Component)

        self.group(n, c)

        self.assertEquals(1, len(n.subject.ownedAttribute))
        self.assertEquals(1, len(n.subject.ownedConnector))
        self.assertEquals(1, len(c.subject.ownedAttribute))
        self.assertEquals(2, len(self.kindof(UML.ConnectorEnd)))

        a1 = n.subject.ownedAttribute[0]
        a2 = c.subject.ownedAttribute[0]

        self.assertTrue(a1.isComposite)
        self.assertTrue(a1 in n.subject.part)

        connector = n.subject.ownedConnector[0]
        self.assertTrue(connector.end[0].role is a1)
        self.assertTrue(connector.end[1].role is a2)


    def test_ungrouping(self):
        """Test decomposition of component from node
        """
        n = self.create(items.NodeItem, UML.Node)
        c = self.create(items.ComponentItem, UML.Component)

        query = self.group(n, c)
        query = self.ungroup(n, c)

        self.assertEquals(0, len(n.subject.ownedAttribute))
        self.assertEquals(0, len(c.subject.ownedAttribute))
        self.assertEquals(0, len(self.kindof(UML.Property)))
        self.assertEquals(0, len(self.kindof(UML.Connector)))
        self.assertEquals(0, len(self.kindof(UML.ConnectorEnd)))


class NodeArtifactGroupTestCase(TestCase):
    def group(self, parent, item):
        """
        Group item within a parent.
        """
        query = (parent, item)
        adapter = component.queryMultiAdapter(query, IGroup)
        adapter.group()


    def ungroup(self, parent, item):
        """
        Remove item from a parent.
        """
        query = (parent, item)
        adapter = component.queryMultiAdapter(query, IGroup)
        adapter.ungroup()


    def test_grouping(self):
        """Test artifact within node deployment
        """
        n = self.create(items.NodeItem, UML.Node)
        a = self.create(items.ArtifactItem, UML.Artifact)

        self.group(n, a)

        self.assertEquals(1, len(n.subject.deployment))
        self.assertTrue(n.subject.deployment[0].deployedArtifact[0] is a.subject)


    def test_ungrouping(self):
        """Test removal of artifact from node
        """
        n = self.create(items.NodeItem, UML.Node)
        a = self.create(items.ArtifactItem, UML.Artifact)

        query = self.group(n, a)
        query = self.ungroup(n, a)

        self.assertEquals(0, len(n.subject.deployment))
        self.assertEquals(0, len(self.kindof(UML.Deployment)))



class SubsystemUseCaseGroupTestCase(TestCase):
    def group(self, parent, item):
        """
        Group item within a parent.
        """
        query = (parent, item)
        adapter = component.queryMultiAdapter(query, IGroup)
        adapter.group()


    def ungroup(self, parent, item):
        """
        Remove item from a parent.
        """
        query = (parent, item)
        adapter = component.queryMultiAdapter(query, IGroup)
        adapter.ungroup()


    def test_grouping(self):
        """Test adding an use case to a subsystem
        """
        s = self.create(items.SubsystemItem, UML.Component)
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)

        self.group(s, uc1)
        self.assertEquals(1, len(uc1.subject.subject))
        self.group(s, uc2)
        self.assertEquals(1, len(uc2.subject.subject))

        self.assertEquals(2, len(s.subject.useCase))


    def test_grouping_with_namespace(self):
        """Test adding an use case to a subsystem (with namespace)
        """
        namespace = NamespaceModel(self.element_factory)
        s = self.create(items.SubsystemItem, UML.Component)
        uc = self.create(items.UseCaseItem, UML.UseCase)

        # manipulate namespace
        c = self.element_factory.create(UML.Class)
        attribute = self.element_factory.create(UML.Property)
        c.ownedAttribute = attribute

        self.group(s, uc)
        self.assertEquals(1, len(uc.subject.subject))
        self.assertTrue(s.subject.namespace is not uc.subject)


    def test_ungrouping(self):
        """Test removal of use case from subsystem
        """
        s = self.create(items.SubsystemItem, UML.Component)
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)

        self.group(s, uc1)
        self.group(s, uc2)

        self.ungroup(s, uc1)
        self.assertEquals(0, len(uc1.subject.subject))
        self.assertEquals(1, len(s.subject.useCase))

        self.ungroup(s, uc2)
        self.assertEquals(0, len(uc2.subject.subject))
        self.assertEquals(0, len(s.subject.useCase))


