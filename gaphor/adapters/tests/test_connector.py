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

    def test_commentline_element(self):
        """
	Test CommentLineItem connecting to comment and Actor items.
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


    def test_commentline_association(self):
        """
        Test CommentLineItem with AssociationItem.

        # TODO: check behaviour if:
          1. comment line is connected to association + comment and after that
             association is connected to two classes.
             -> association should be connected to comment.annotatedElement
          2. association is disconnected while a comment is connected:
             -> association should be removed from comment.annotatedElement
        """
        diagram = UML.create(UML.Diagram)
        comment = diagram.create(items.CommentItem, subject=UML.create(UML.Comment))
        line = diagram.create(items.CommentLineItem)
        line.head.pos = 100, 100
        line.tail.pos = 100, 100
        c1 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        c2 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        assoc = diagram.create(items.AssociationItem)

        adapter = component.queryMultiAdapter((c1, assoc), IConnect)
        handle = assoc.head
        adapter.connect(handle, handle.x, handle.y)

        adapter = component.queryMultiAdapter((c2, assoc), IConnect)
        handle = assoc.tail
        adapter.connect(handle, handle.x, handle.y)

        assert assoc.head.connected_to is c1
        assert assoc.tail.connected_to is c2
        assert assoc.subject

        # Connect the association item to the head of the line:

        adapter = component.queryMultiAdapter((assoc, line), IConnect)
        assert adapter
        assert type(adapter) is gaphor.adapters.connectors.CommentLineLineConnect
        handle = line.head
        pos = adapter.glue(handle, handle.x, handle.y)
        assert pos == (0, 10), pos
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is assoc
        assert handle._connect_constraint is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.tail
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is None
        assert not hasattr(handle,'_connect_constraint')
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        # now connect the comment

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.tail
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is comment
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect comment:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle._connect_constraint is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Connect again:

        adapter.connect(handle, handle.x, handle.y)
        assert handle.connected_to is not None, handle.connected_to


    def test_connector_association_connect(self):
        """
        Test behaviour when the CommentLine's subject (association) is
        connected after the comment line is connected.
        """
        diagram = UML.create(UML.Diagram)
        comment = diagram.create(items.CommentItem, subject=UML.create(UML.Comment))
        line = diagram.create(items.CommentLineItem)
        line.head.pos = 100, 100
        line.tail.pos = 100, 100
        c1 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        c2 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        assoc = diagram.create(items.AssociationItem)

        # connect the comment

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.tail
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is comment
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement

        # connect opposite end to the association:

        adapter = component.queryMultiAdapter((assoc, line), IConnect)
        handle = line.head
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is assoc
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert assoc.subject is None

        # Now connect the association to the classes:

        adapter = component.queryMultiAdapter((c1, assoc), IConnect)
        handle = assoc.head
        adapter.connect(handle, handle.x, handle.y)

        assert handle.connected_to is c1
        assert handle._connect_constraint is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert assoc.subject is None

        adapter = component.queryMultiAdapter((c2, assoc), IConnect)
        handle = assoc.tail
        adapter.connect(handle, handle.x, handle.y)

        assert assoc.head.connected_to is c1
        assert assoc.tail.connected_to is c2
        assert assoc.subject
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert assoc.subject in comment.subject.annotatedElement

        # And now disconnect the association (comment.annotatedElement should
        # also become empty:

        adapter.disconnect(handle)
        assert assoc.tail.connected_to is None
        assert assoc.subject is None
        assert comment.subject is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement

        # TODO: add test
        # What happens when an association is displayed in two diagrams and
        # the comment is connected in one diagram. That assoc. is broken.


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

    def test_extension(self):
        assert len(list(UML.select())) == 0

        diagram = UML.create(UML.Diagram)
        gen = diagram.create(items.ExtensionItem)
        c1 = diagram.create(items.ClassItem, subject=UML.create(UML.Stereotype))
        c2 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))

        assert len(list(UML.select())) == 3

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail, gen.tail.x, gen.tail.y)

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head, gen.head.x, gen.head.y)

        assert gen.head.connected_to is c2
        assert gen.subject is not None
        
        assert len(list(UML.select())) == 6

        adapter.disconnect(gen.head)

        assert len(list(UML.select())) == 3, list(UML.select())

    def test_association(self):
        assert len(list(UML.select())) == 0

        diagram = UML.create(UML.Diagram)
        gen = diagram.create(items.AssociationItem)
        c1 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        c2 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))

        assert len(list(UML.select())) == 3

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail, gen.tail.x, gen.tail.y)

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head, gen.head.x, gen.head.y)

        assert gen.head.connected_to is c2
        assert gen.subject is not None
        
        # Diagram, Class x2, Property *2, Association, LiteralSpec *2
        assert len(list(UML.select())) == 8, list(UML.select())
        assert gen.head_end.subject is not None
        assert gen.tail_end.subject is not None
        assert gen.head_end._name_bounds.width == 10
        assert gen.tail_end._name_bounds.width == 10

        gen.head_end.subject.name = 'cheese'
        assert gen.head_end._name_bounds.width > 10, gen.head_end._name_bounds.width

        adapter.disconnect(gen.head)

        assert len(list(UML.select())) == 3, list(UML.select())

    def test_flow_activitynodes(self):
        assert len(list(UML.select())) == 0

        diagram = UML.create(UML.Diagram)
        flow = diagram.create(items.FlowItem)
        i1 = diagram.create(items.InitialNodeItem, subject=UML.create(UML.InitialNode))
        f1 = diagram.create(items.ActivityFinalNodeItem, subject=UML.create(UML.ActivityFinalNode))
        f2 = diagram.create(items.FlowFinalNodeItem, subject=UML.create(UML.FlowFinalNode))

        assert len(UML.lselect()) == 4

        # head may not connect to FinalNode

        adapter = component.queryMultiAdapter((f1, flow), IConnect)
        assert adapter
        adapter.connect(flow.head, flow.head.x, flow.head.y)
        assert flow.head.connected_to is None

        adapter.connect(flow.tail, flow.tail.x, flow.tail.y)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is f1

        adapter.disconnect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is None

        adapter = component.queryMultiAdapter((f2, flow), IConnect)
        assert adapter
        adapter.connect(flow.head, flow.head.x, flow.head.y)
        assert flow.head.connected_to is None

        adapter.connect(flow.tail, flow.tail.x, flow.tail.y)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is f2

        adapter.disconnect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is None

        # tail may not connect to InitialNode

        adapter = component.queryMultiAdapter((i1, flow), IConnect)
        assert adapter
        adapter.connect(flow.tail, flow.tail.x, flow.tail.y)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is None

        adapter.connect(flow.head, flow.head.x, flow.head.y)
        assert flow.tail.connected_to is None
        assert flow.head.connected_to is i1

    
    def test_flow_action(self):
        assert len(list(UML.select())) == 0

        diagram = UML.create(UML.Diagram)
        flow = diagram.create(items.FlowItem)
        a1 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        a2 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        o1 = diagram.create(items.ObjectNodeItem, subject=UML.create(UML.ObjectNode))

        assert len(UML.lselect()) == 5, UML.lselect()

        # Connect between two actions (ControlFlow)
        adapter = component.queryMultiAdapter((a1, flow), IConnect)
        assert adapter
        adapter.connect(flow.tail, flow.tail.x, flow.tail.y)

        assert flow.tail.connected_to is a1
        assert flow.subject is None

        adapter = component.queryMultiAdapter((a2, flow), IConnect)
        adapter.connect(flow.head, flow.head.x, flow.head.y)

        assert flow.head.connected_to is a2
        assert flow.tail.connected_to is a1
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ControlFlow)

        adapter.connect(flow.tail, flow.tail.x, flow.tail.y)

        assert flow.head.connected_to is a2
        assert flow.tail.connected_to is a2
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ControlFlow)

        # Connection between action and objectNode (ObjectFlow)

        adapter = component.queryMultiAdapter((o1, flow), IConnect)
        adapter.connect(flow.head, flow.head.x, flow.head.y)

        assert flow.head.connected_to is o1
        assert flow.tail.connected_to is a2
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ObjectFlow)

        adapter.disconnect(flow.head)

        assert flow.head.connected_to is None
        assert flow.tail.connected_to is a2
        assert flow.subject is None

    def test_flow_connect(self):
        assert len(list(UML.select())) == 0

        diagram = UML.create(UML.Diagram)
        flow1 = diagram.create(items.FlowItem)
        flow2 = diagram.create(items.FlowItem)
        a1 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        a2 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        o1 = diagram.create(items.ObjectNodeItem, subject=UML.create(UML.ObjectNode))

        assert len(UML.lselect()) == 5, UML.lselect()

        adapter = component.queryMultiAdapter((a1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.tail, flow1.tail.x, flow1.tail.y)
        assert flow1.tail.connected_to is a1
        assert not a1.subject.incoming, a1.subject.incoming

        # More than one edge may be connected to an action:

        adapter = component.queryMultiAdapter((a1, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.tail, flow2.tail.x, flow2.tail.y)
        assert flow1.tail.connected_to is a1
        assert flow2.tail.connected_to is a1

        adapter = component.queryMultiAdapter((a2, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.head, flow1.head.x, flow1.head.y)
        assert flow1.head.connected_to is a2
        assert flow1.tail.connected_to is a1
        assert flow1.subject in a1.subject.incoming
        assert flow1.subject.target is a1.subject
        assert flow1.subject in a2.subject.outgoing
        assert flow1.subject.source is a2.subject

    def test_flow_fork_decision(self, itemClass=items.ForkNodeItem, forkNodeClass=UML.ForkNode, joinNodeClass=UML.JoinNode):
        """
        Test fork/decision behaviour.
         [1] A join node has one outgoing edge.
             self.outgoing->size() = 1
         [2] If a join node has an incoming object flow, it must have an
             outgoing object flow, otherwise, it must have an outgoing control
             flow.

         [1] A fork node has one incoming edge.
         [2] The edges coming into and out of a fork node must be either all
             object flows or all control flows.
        """
        assert len(list(UML.select())) == 0

        diagram = UML.create(UML.Diagram)
        flow1 = diagram.create(items.FlowItem)
        flow2 = diagram.create(items.FlowItem)
        flow3 = diagram.create(items.FlowItem)
        flow4 = diagram.create(items.FlowItem)
        a1 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        a2 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        a3 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        a4 = diagram.create(items.ActionItem, subject=UML.create(UML.Action))
        f1 = diagram.create(itemClass, subject=UML.create(joinNodeClass))

        #assert len(UML.lselect()) == 6, UML.lselect()

        # Connect between two actions (ControlFlow)
        # Connecting line this:
        #        head  tail|--flow2-->[ a2 ]
        # [ a1 ] --flow1-->|
        #                  |--flow3-->[ a3 ]

        # First connect the Actions:

        adapter = component.queryMultiAdapter((a1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.head, flow1.head.x, flow1.head.y)

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.tail, flow2.tail.x, flow2.tail.y)

        adapter = component.queryMultiAdapter((a3, flow3), IConnect)
        assert adapter
        adapter.connect(flow3.tail, flow3.tail.x, flow3.tail.y)

        # Now connect to ForkNode:

        adapter = component.queryMultiAdapter((f1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.tail, flow1.tail.x, flow1.tail.y)
        assert flow1.tail.connected_to is f1
        assert flow1.subject
        assert flow1.subject.target is f1.subject
        assert flow1.subject in f1.subject.incoming
        assert type(f1.subject) is joinNodeClass

        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.head, flow2.head.x, flow2.head.y)
        assert flow2.head.connected_to is f1
        assert flow2.subject.source is f1.subject
        assert flow2.subject in f1.subject.outgoing
        assert type(f1.subject) is joinNodeClass
        assert flow2.canvas

        adapter = component.queryMultiAdapter((f1, flow3), IConnect)
        assert adapter
        adapter.connect(flow3.head, flow3.head.x, flow3.head.y)
        assert flow3.head.connected_to is f1
        assert flow3.subject.source is f1.subject
        assert flow3.subject in f1.subject.outgoing
        assert len(f1.subject.outgoing) == 2

        assert type(f1.subject) is forkNodeClass, f1.subject

        # flow4 will force the forknode to become a combined node:

        adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        assert adapter
        adapter.connect(flow4.tail, flow4.tail.x, flow4.tail.y)
        assert type(f1.subject) is forkNodeClass

        adapter = component.queryMultiAdapter((a4, flow4), IConnect)
        adapter.connect(flow4.head, flow4.head.x, flow4.head.y)
        assert type(f1.subject) is joinNodeClass
        assert f1.combined
        assert flow4.tail.connected_to is f1
        assert flow4.subject.target is f1.subject
        assert type(f1.combined) is forkNodeClass, f1.combined
        assert flow1.subject in f1.subject.incoming
        assert flow4.subject in f1.subject.incoming
        assert flow2.subject in f1.combined.outgoing, f1.combined.outgoing
        assert flow3.subject in f1.combined.outgoing, f1.combined.outgoing
        assert len(f1.subject.outgoing) == 1
        assert len(f1.combined.incoming) == 1
        assert f1.subject.outgoing[0] is f1.combined.incoming[0]

        # flow4 can be connected as outgoing flow though:
        #adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        #assert adapter
        #adapter.connect(flow4.head, flow4.head.x, flow4.head.y)
        #assert flow4.head.connected_to is f1

        adapter.disconnect(flow4.head)
        assert flow4.head.connected_to is None
        adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        adapter.disconnect(flow4.tail)
        assert not f1.combined
        
        assert flow2.canvas
        assert flow2.canvas.solver

        # Now change the ForkNode back into a JoinNode by moving flow2
        # to the opposite side:
        # [ a1 ]--flow1-->|
        #                 |--flow3-->[ a3 ]
        # [ a2 ]--flow2-->|

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        adapter.disconnect(flow2.tail)
        assert len(a2.subject.incoming) == 0

        # Let's try if we can connect both ends of flow2 to the ForkNode:
        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        adapter.connect(flow2.tail, flow2.tail.x, flow2.tail.y)
        assert flow2.tail.connected_to is None, flow2.tail.connected_to

        adapter.disconnect(flow2.head)
        assert len(f1.subject.incoming) == 1
        assert len(f1.subject.outgoing) == 1

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        adapter.connect(flow2.head, flow2.head.x, flow2.head.y)
        assert len(a2.subject.outgoing) == 0

        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        adapter.connect(flow2.tail, flow2.tail.x, flow2.tail.y)
        assert len(a2.subject.outgoing) == 1
        assert len(f1.subject.incoming) == 2
        assert len(f1.subject.outgoing) == 1
        assert type(f1.subject) is joinNodeClass, f1.subject

        # And of course I can't add another outgoing edge:
        #adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        #assert adapter
        #adapter.connect(flow4.head, flow4.head.x, flow4.head.y)
        #assert flow4.head.connected_to is None


    def test_flow_decision_merge(self):
        """
        Decision/Merge node is basically the same as Fork/Join node.
        """
        self.test_flow_fork_decision(itemClass=items.DecisionNodeItem,
                                     forkNodeClass=UML.DecisionNode,
                                     joinNodeClass=UML.MergeNode)

# vim:sw=4:et:ai
