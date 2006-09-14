"""
Test Item connections.
"""

import unittest
from zope import component
from gaphor import resource
from gaphor import UML
from gaphor.ui.mainwindow import MainWindow
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem
from gaphor.diagram.actor import ActorItem
from gaphor.diagram.dependency import DependencyItem
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
        comment = diagram.create(CommentItem, subject=UML.create(UML.Comment))
        line = diagram.create(CommentLineItem)
        actor = diagram.create(ActorItem, subject=UML.create(UML.Actor))
        actor2 = diagram.create(ActorItem, subject=UML.create(UML.Actor))

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
        actor1 = diagram.create(ActorItem, subject=UML.create(UML.Actor))
        actor2 = diagram.create(ActorItem, subject=UML.create(UML.Actor))
        dep = diagram.create(DependencyItem)

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

        #iface1 = diagram.create(InterfaceItem, subject=UML.Interface)

        adapter.connect(dep.tail, dep.tail.x, dep.tail.y)

        assert dep.subject is not None
        assert dep.subject is not dep_subj # the old subject has been deleted
        assert dep.subject in actor1.subject.supplierDependency
        assert dep.subject in actor2.subject.clientDependency
        
        # TODO: test with interface (usage) and component (realization)

        # TODO: test with multiple diagrams (should reuse existing relationships first)

    def test_implementation(self):
        pass

#vi:sw=4:et:ai
