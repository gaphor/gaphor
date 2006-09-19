"""
Test Item connections.
"""

import unittest
from zope import component
from gaphor import resource
from gaphor import UML
from gaphor.ui.mainwindow import MainWindow
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

# Ensure adapters are loaded
import gaphor.adapters

class ConnectorTestCase(unittest.TestCase):

    def tearDown(self):
        UML.flush()

    def test_commentline(self):
        """Test CommentLineItem connecting to comment and Actor items.
        """
        diagram = UML.create(UML.Diagram)
        comment = diagram.create(items.CommentItem, subject=UML.create(UML.Comment))
        line = diagram.create(items.CommentLineItem)
        actor = diagram.create(items.ActorItem, subject=UML.create(UML.Actor))
        actor2 = diagram.create(items.ActorItem, subject=UML.create(UML.Actor))

        # Connect the comment item to the head of the line:

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.head
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is comment
        assert handle._connect_constraint is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.tail
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is None
        assert not hasattr(handle,'_connect_constraint')
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        #print '# now connect the actor'

        adapter = component.queryMultiAdapter((actor, line), IConnect)

        handle = line.handles()[-1]
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is actor
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Same thing with another actor
        # (should disconnect the already connected actor):

        handle = line.tail
        adapter = component.queryMultiAdapter((actor2, line), IConnect)
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is actor2
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect actor:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle._connect_constraint is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement


    def test_dependency(self):
        diagram = UML.create(UML.Diagram)
        actor1 = diagram.create(items.ActorItem, subject=UML.create(UML.Actor))
        actor2 = diagram.create(items.ActorItem, subject=UML.create(UML.Actor))
        dep = diagram.create(items.DependencyItem)

        adapter = component.queryMultiAdapter((actor1, dep), IConnect)

        adapter.connect(dep.head, dep.head.x, dep.head.y)

        assert dep.subject is None
        assert dep.head.connected_to is actor1

        adapter = component.queryMultiAdapter((actor2, dep), IConnect)

        adapter.connect(dep.tail, dep.tail.x, dep.tail.y)

        assert dep.subject is not None
        assert isinstance(dep.subject, UML.Dependency), dep.subject
        assert dep.subject in UML.select()
        assert dep.head.connected_to is actor1
        assert dep.tail.connected_to is actor2

        assert actor1.subject in dep.subject.supplier
        assert actor2.subject in dep.subject.client

        # Disconnect client side
        dep_subj = dep.subject
        adapter.disconnect(dep.tail)

        assert dep.subject is None
        assert dep.tail.connected_to is None
        assert dep_subj not in UML.select()
        assert dep_subj not in actor1.subject.supplierDependency
        assert dep_subj not in actor2.subject.clientDependency

        #iface1 = diagram.create(items.InterfaceItem, subject=UML.Interface)

        adapter.connect(dep.tail, dep.tail.x, dep.tail.y)

        assert dep.subject is not None
        assert dep.subject is not dep_subj # the old subject has been deleted
        assert dep.subject in actor1.subject.supplierDependency
        assert dep.subject in actor2.subject.clientDependency
        
        # TODO: test with interface (usage) and component (realization)

        # TODO: test with multiple diagrams (should reuse existing relationships first)

    def test_multi_dependency(self):
        """Dependency should appear in a new diagram, bound on a new
        DependencyItem.
        """
        diagram = UML.create(UML.Diagram)
        actor1 = UML.create(UML.Actor)
        actor2 = UML.create(UML.Actor)
        actoritem1 = diagram.create(items.ActorItem, subject=actor1)
        actoritem2 = diagram.create(items.ActorItem, subject=actor2)
        dep = diagram.create(items.DependencyItem)
        
        adapter = component.queryMultiAdapter((actoritem1, dep), IConnect)

        adapter.connect(dep.head, dep.head.x, dep.head.y)

        adapter = component.queryMultiAdapter((actoritem2, dep), IConnect)

        adapter.connect(dep.tail, dep.tail.x, dep.tail.y)

        assert dep.subject
        assert len(actor1.supplierDependency) == 1
        assert actor1.supplierDependency[0] is dep.subject
        assert len(actor2.clientDependency) == 1
        assert actor2.clientDependency[0] is dep.subject

        # Do the same thing, but now on a new diagram:

        diagram2 = UML.create(UML.Diagram)
        actoritem3 = diagram2.create(items.ActorItem, subject=actor1)
        actoritem4 = diagram2.create(items.ActorItem, subject=actor2)
        dep2 = diagram2.create(items.DependencyItem)

        adapter = component.queryMultiAdapter((actoritem3, dep2), IConnect)

        adapter.connect(dep2.head, dep2.head.x, dep2.head.y)

        adapter = component.queryMultiAdapter((actoritem4, dep2), IConnect)

        adapter.connect(dep2.tail, dep2.tail.x, dep2.tail.y)

        assert dep2.subject
        assert len(actor1.supplierDependency) == 1
        assert actor1.supplierDependency[0] is dep.subject
        assert len(actor2.clientDependency) == 1
        assert actor2.clientDependency[0] is dep.subject

        assert dep.subject is dep2.subject

    def test_implementation(self):
        diagram = UML.create(UML.Diagram)
        impl = diagram.create(items.ImplementationItem)
        clazz = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        iface = diagram.create(items.InterfaceItem, subject=UML.create(UML.Interface))

        adapter = component.queryMultiAdapter((clazz, impl), IConnect)

        adapter.connect(impl.head, impl.head.x, impl.head.y)

        # Should not be allowed to connect to anything but Interfaces

        assert impl.head.connected_to is None

        adapter.connect(impl.tail, impl.tail.x, impl.tail.y)
        assert impl.tail.connected_to is clazz
        assert impl.subject is None

        adapter = component.queryMultiAdapter((iface, impl), IConnect)

        adapter.connect(impl.head, impl.head.x, impl.head.y)

        assert impl.head.connected_to is iface
        assert impl.subject is not None
        assert impl.subject.contract[0] is iface.subject
        assert impl.subject.implementatingClassifier[0] is clazz.subject

    def test_generalization(self):
        diagram = UML.create(UML.Diagram)
        gen = diagram.create(items.GeneralizationItem)
        c1 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        c2 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail, gen.tail.x, gen.tail.y)

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head, gen.head.x, gen.head.y)

        assert gen.head.connected_to is c2
        assert gen.subject is not None
        assert gen.subject.general is c2.subject
        assert gen.subject.specific is c1.subject


#vi:sw=4:et:ai
