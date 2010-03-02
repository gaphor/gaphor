"""
Classes related adapter connection tests.
"""

from gaphas.canvas import ConnectionError
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items

class DependencyTestCase(TestCase):
    """
    Dependency item connection adapter tests.
    """
    def test_dependency_glue(self):
        """Test dependency glue to two actor items
        """
        actor1 = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)
        dep = self.create(items.DependencyItem)

        glued = self.allow(dep, dep.head, actor1)
        self.assertTrue(glued)

        self.connect(dep, dep.head, actor1)

        glued = self.allow(dep, dep.tail, actor2)
        self.assertTrue(glued)


    def test_dependency_connect(self):
        """Test dependency connecting to two actor items
        """
        actor1 = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)
        dep = self.create(items.DependencyItem)

        self.connect(dep, dep.head, actor1)
        self.connect(dep, dep.tail, actor2)

        self.assertTrue(dep.subject is not None)
        self.assertTrue(isinstance(dep.subject, UML.Dependency))
        self.assertTrue(dep.subject in self.element_factory.select())

        hct = self.get_connected(dep.head)
        tct = self.get_connected(dep.tail)
        self.assertTrue(hct is actor1)
        self.assertTrue(tct is actor2)

        self.assertTrue(actor1.subject in dep.subject.supplier)
        self.assertTrue(actor2.subject in dep.subject.client)


    def test_dependency_reconnection(self):
        """Test dependency reconnection
        """
        a1 = self.create(items.ActorItem, UML.Actor)
        a2 = self.create(items.ActorItem, UML.Actor)
        a3 = self.create(items.ActorItem, UML.Actor)
        dep = self.create(items.DependencyItem)

        # connect: a1 -> a2
        self.connect(dep, dep.head, a1)
        self.connect(dep, dep.tail, a2)

        d = dep.subject

        # reconnect: a1 -> a3
        self.connect(dep, dep.tail, a3)

        self.assertSame(d, dep.subject)
        self.assertEquals(1, len(dep.subject.supplier))
        self.assertEquals(1, len(dep.subject.client))
        self.assertTrue(a1.subject in dep.subject.supplier)
        self.assertTrue(a3.subject in dep.subject.client)
        self.assertTrue(a2.subject not in dep.subject.client, dep.subject.client)


    def test_dependency_disconnect(self):
        """Test dependency disconnecting using two actor items
        """
        actor1 = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)
        dep = self.create(items.DependencyItem)

        self.connect(dep, dep.head, actor1)
        self.connect(dep, dep.tail, actor2)

        dep_subj = dep.subject
        self.disconnect(dep, dep.tail)

        self.assertTrue(dep.subject is None)
        self.assertTrue(self.get_connected(dep.tail) is None)
        self.assertTrue(dep_subj not in self.element_factory.select())
        self.assertTrue(dep_subj not in actor1.subject.supplierDependency)
        self.assertTrue(dep_subj not in actor2.subject.clientDependency)


    def test_dependency_reconnect(self):
        """Test dependency reconnection using two actor items
        """
        actor1 = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)
        dep = self.create(items.DependencyItem)

        self.connect(dep, dep.head, actor1)
        self.connect(dep, dep.tail, actor2)

        dep_subj = dep.subject
        self.disconnect(dep, dep.tail)

        # reconnect
        self.connect(dep, dep.tail, actor2)

        self.assertTrue(dep.subject is not None)
        self.assertTrue(dep.subject is not dep_subj) # the old subject has been deleted
        self.assertTrue(dep.subject in actor1.subject.supplierDependency)
        self.assertTrue(dep.subject in actor2.subject.clientDependency)
        # TODO: test with interface (usage) and component (realization)
        # TODO: test with multiple diagrams (should reuse existing relationships first)


    def test_multi_dependency(self):
        """Test multiple dependencies
        
        Dependency should appear in a new diagram, bound on a new
        dependency item.
        """
        actoritem1 = self.create(items.ActorItem, UML.Actor)
        actoritem2 = self.create(items.ActorItem, UML.Actor)
        actor1 = actoritem1.subject
        actor2 = actoritem2.subject
        dep = self.create(items.DependencyItem)
        
        self.connect(dep, dep.head, actoritem1)
        self.connect(dep, dep.tail, actoritem2)

        self.assertTrue(dep.subject)
        self.assertEquals(1, len(actor1.supplierDependency))
        self.assertTrue(actor1.supplierDependency[0] is dep.subject)
        self.assertEquals(1, len(actor2.clientDependency))
        self.assertTrue(actor2.clientDependency[0] is dep.subject)

        # Do the same thing, but now on a new diagram:

        diagram2 = self.element_factory.create(UML.Diagram)
        actoritem3 = diagram2.create(items.ActorItem, subject=actor1)
        actoritem4 = diagram2.create(items.ActorItem, subject=actor2)
        dep2 = diagram2.create(items.DependencyItem)

        self.connect(dep2, dep2.head, actoritem3)
        cinfo = diagram2.canvas.get_connection(dep2.head)
        self.assertNotSame(None, cinfo)
        self.assertSame(cinfo.connected, actoritem3)
        self.connect(dep2, dep2.tail, actoritem4)
        self.assertNotSame(dep2.subject, None)
        self.assertEquals(1, len(actor1.supplierDependency))
        self.assertTrue(actor1.supplierDependency[0] is dep.subject)
        self.assertEquals(1, len(actor2.clientDependency))
        self.assertTrue(actor2.clientDependency[0] is dep.subject)

        self.assertSame(dep.subject, dep2.subject)


    def test_dependency_type_auto(self):
        """Test dependency type automatic determination
        """
        cls = self.create(items.ClassItem, UML.Class)
        iface = self.create(items.InterfaceItem, UML.Interface)
        dep = self.create(items.DependencyItem)

        assert dep.auto_dependency

        self.connect(dep, dep.tail, cls) # connect client
        self.connect(dep, dep.head, iface) # connect supplier

        self.assertTrue(dep.subject is not None)
        self.assertTrue(isinstance(dep.subject, UML.Usage), dep.subject)
        self.assertTrue(dep.subject in self.element_factory.select())


class GeneralizationTestCase(TestCase):
    """
    Generalization item connection adapter tests.
    """
    def test_glue(self):
        """Test generalization item glueing using two classes
        """
        gen = self.create(items.GeneralizationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        glued = self.allow(gen, gen.tail, c1)
        self.assertTrue(glued)

        self.connect(gen, gen.tail, c1)
        self.assertTrue(self.get_connected(gen.tail) is c1)
        self.assertTrue(gen.subject is None)

        glued = self.allow(gen, gen.head, c2)
        self.assertTrue(glued)


    def test_connection(self):
        """Test generalization item connection using two classes
        """
        gen = self.create(items.GeneralizationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        self.connect(gen, gen.tail, c1)
        assert self.get_connected(gen.tail) is c1

        self.connect(gen, gen.head, c2)
        self.assertTrue(gen.subject is not None)
        self.assertTrue(gen.subject.general is c2.subject)
        self.assertTrue(gen.subject.specific is c1.subject)

    def test_reconnection(self):
        """Test generalization item connection using two classes

        On reconnection a new Generalization is created.
        """
        gen = self.create(items.GeneralizationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        self.connect(gen, gen.tail, c1)
        assert self.get_connected(gen.tail) is c1

        self.connect(gen, gen.head, c2)
        self.assertTrue(gen.subject is not None)
        self.assertTrue(gen.subject.general is c2.subject)
        self.assertTrue(gen.subject.specific is c1.subject)

        # Now do the same on a new diagram:
        diagram2 = self.element_factory.create(UML.Diagram)
        c3 = diagram2.create(items.ClassItem, subject=c1.subject)
        c4 = diagram2.create(items.ClassItem, subject=c2.subject)
        gen2 = diagram2.create(items.GeneralizationItem)

        self.connect(gen2, gen2.head, c3)
        cinfo = diagram2.canvas.get_connection(gen2.head)
        self.assertNotSame(None, cinfo)
        self.assertSame(cinfo.connected, c3)

        self.connect(gen2, gen2.tail, c4)
        self.assertNotSame(gen.subject, gen2.subject)
        self.assertEquals(1, len(c1.subject.generalization))
        self.assertSame(c1.subject.generalization[0], gen.subject)
        #self.assertEquals(1, len(actor2.clientDependency))
        #self.assertTrue(actor2.clientDependency[0] is dep.subject)


class AssociationConnectorTestCase(TestCase):
    """
    Association item connection adapters tests.
    """
    def test_glue(self):
        """Test association item glue
        """
        asc = self.create(items.AssociationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        glued = self.allow(asc, asc.head, c1)
        self.assertTrue(glued)

        self.connect(asc, asc.head, c1)

        glued = self.allow(asc, asc.tail, c2)
        self.assertTrue(glued)


    def test_connect(self):
        """Test association item connection
        """
        asc = self.create(items.AssociationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        self.connect(asc, asc.head, c1)
        self.assertTrue(asc.subject is None) # no UML metaclass yet

        self.connect(asc, asc.tail, c2)
        self.assertTrue(asc.subject is not None)
        
        # Diagram, Class *2, Property *2, Association, LiteralSpec *2
        self.assertEquals(8, len(list(self.element_factory.select())))
        self.assertTrue(asc.head_end.subject is not None)
        self.assertTrue(asc.tail_end.subject is not None)


    def test_reconnect(self):
        """Test association item reconnection
        """
        asc = self.create(items.AssociationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)
        c3 = self.create(items.ClassItem, UML.Class)

        self.connect(asc, asc.head, c1)
        self.assertTrue(asc.subject is None) # no UML metaclass yet

        self.connect(asc, asc.tail, c2)
        self.assertTrue(asc.subject is not None)
        a = asc.subject

        self.assertRaises(ConnectionError, self.connect, asc, asc.tail, c3)

        self.disconnect(asc, asc.tail)
        self.connect(asc, asc.tail, c3)
        self.assertTrue(asc.subject is not None)
        self.assertTrue(asc.subject is not a)


    def test_disconnect(self):
        """Test association item disconnection
        """
        asc = self.create(items.AssociationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        self.connect(asc, asc.head, c1)
        self.assertTrue(asc.subject is None) # no UML metaclass yet

        self.connect(asc, asc.tail, c2)
        assert asc.subject is not None

        self.disconnect(asc, asc.head)
        
        # after disconnection: one diagram and two classes
        self.assertEquals(3, len(list(self.element_factory.select())))


# vim:sw=4:et:ai
