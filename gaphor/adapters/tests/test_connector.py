"""
Test Item connections.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

class ConnectorTestCase(TestCase):

    services = ['element_factory', 'adapter_loader']

    def test_commentline_element(self):
        """
	Test CommentLineItem connecting to comment and Actor items.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        actor = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)

        # Connect the comment item to the head of the line:

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.head
        adapter.connect(handle)

        assert handle.connected_to is comment
        assert handle.connection_data is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is None, handle.connected_to
        #assert not hasattr(handle,'connection_constraint')
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        # now connect the actor

        adapter = component.queryMultiAdapter((actor, line), IConnect)

        handle = line.handles()[-1]
        adapter.connect(handle)

        assert handle.connected_to is actor
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Same thing with another actor
        # (should disconnect the already connected actor):

        handle = line.tail
        adapter = component.queryMultiAdapter((actor2, line), IConnect)
        adapter.connect(handle)

        assert handle.connected_to is actor2
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect actor:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle.connection_data is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not actor2.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.head
        adapter.disconnect(handle)
        

    def test_commentline_class(self):
        """
        Connect a CommentLine to a class and unlink the commentLine
        afterwards.
        """
        clazz = self.create(items.ClassItem, UML.Class)
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        adapter = component.queryMultiAdapter((comment, line), IConnect)
        handle = line.head
        adapter.connect(handle)

        adapter = component.queryMultiAdapter((clazz, line), IConnect)
        handle = line.tail
        adapter.connect(handle)

        assert clazz.subject in comment.subject.annotatedElement
        assert comment.subject in clazz.subject.ownedComment

        line.unlink()

        assert not comment.subject.annotatedElement
        assert not clazz.subject.ownedComment


    def test_commentline_relationship_unlink(self):
        """
        Connect a CommentLine to a relationship item.
        Removing the relationship should work.

        Demonstrates defect #103.
        """
        clazz1 = self.create(items.ClassItem, UML.Class)
        clazz2 = self.create(items.ClassItem, UML.Class)
        gen = self.create(items.GeneralizationItem)

        adapter = component.queryMultiAdapter((clazz1, gen), IConnect)
        handle = gen.head
        adapter.connect(handle)

        adapter = component.queryMultiAdapter((clazz2, gen), IConnect)
        handle = gen.tail
        adapter.connect(handle)

        assert gen.subject

        # And now the comment:

        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        adapter = component.queryMultiAdapter((comment, line), IConnect)
        handle = line.head
        adapter.connect(handle)

        adapter = component.queryMultiAdapter((gen, line), IConnect)
        handle = line.tail
        adapter.connect(handle)

        assert gen.subject in comment.subject.annotatedElement
        assert comment.subject in gen.subject.ownedComment

        gen.unlink()

        assert not comment.subject.annotatedElement
        assert not gen.subject


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
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        line.head.pos = 100, 100
        line.tail.pos = 100, 100
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)
        assoc = self.create(items.AssociationItem)

        adapter = component.queryMultiAdapter((c1, assoc), IConnect)
        handle = assoc.head
        adapter.connect(handle)

        adapter = component.queryMultiAdapter((c2, assoc), IConnect)
        handle = assoc.tail
        adapter.connect(handle) 
        assert assoc.head.connected_to is c1
        assert assoc.tail.connected_to is c2
        assert assoc.subject

        # Connect the association item to the head of the line:

        adapter = component.queryMultiAdapter((assoc, line), IConnect)
        assert adapter
        import gaphor.adapters.connectors
        assert type(adapter) is gaphor.adapters.connectors.CommentLineLineConnect
        handle = line.head
        pos = adapter.glue(handle)
        assert pos == (10, 50), pos
        adapter.connect(handle)

        assert handle.connected_to is assoc
        assert handle.connection_data is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is None
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        # now connect the comment

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is comment
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect comment:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle.connection_data is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Connect again:

        adapter.connect(handle)
        assert handle.connected_to is not None, handle.connected_to


    def test_connector_association_connect(self):
        """
        Test behaviour when the CommentLine's subject (association) is
        connected after the comment line is connected.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        line.head.pos = 100, 100
        line.tail.pos = 100, 100
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)
        assoc = self.create(items.AssociationItem)

        # connect the comment

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is comment
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement

        # connect opposite end to the association:

        adapter = component.queryMultiAdapter((assoc, line), IConnect)
        handle = line.head
        adapter.connect(handle)

        assert handle.connected_to is assoc
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert assoc.subject is None

        # Now connect the association to the classes:

        adapter = component.queryMultiAdapter((c1, assoc), IConnect)
        handle = assoc.head
        adapter.connect(handle)

        assert handle.connected_to is c1
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert assoc.subject is None

        adapter = component.queryMultiAdapter((c2, assoc), IConnect)
        handle = assoc.tail
        adapter.connect(handle)

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
        actor1 = self.create(items.ActorItem, UML.Actor)
        actor2 = self.create(items.ActorItem, UML.Actor)
        dep = self.create(items.DependencyItem)

        adapter = component.queryMultiAdapter((actor1, dep), IConnect)

        adapter.connect(dep.head)

        assert dep.subject is None
        assert dep.head.connected_to is actor1

        adapter = component.queryMultiAdapter((actor2, dep), IConnect)

        adapter.connect(dep.tail)

        assert dep.subject is not None
        assert isinstance(dep.subject, UML.Dependency), dep.subject
        assert dep.subject in self.element_factory.select(), self.element_factory.lselect()
        assert dep.head.connected_to is actor1
        assert dep.tail.connected_to is actor2

        assert actor1.subject in dep.subject.supplier
        assert actor2.subject in dep.subject.client

        # Disconnect client side
        dep_subj = dep.subject
        adapter.disconnect(dep.tail)

        assert dep.subject is None
        assert dep.tail.connected_to is None
        assert dep_subj not in self.element_factory.select()
        assert dep_subj not in actor1.subject.supplierDependency
        assert dep_subj not in actor2.subject.clientDependency

        #iface1 = self.create(items.InterfaceItem, UML.Interface)

        adapter.connect(dep.tail)

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
        actoritem1 = self.create(items.ActorItem, UML.Actor)
        actoritem2 = self.create(items.ActorItem, UML.Actor)
        actor1 = actoritem1.subject
        actor2 = actoritem2.subject
        dep = self.create(items.DependencyItem)
        
        adapter = component.queryMultiAdapter((actoritem1, dep), IConnect)

        adapter.connect(dep.head)

        adapter = component.queryMultiAdapter((actoritem2, dep), IConnect)

        adapter.connect(dep.tail)

        assert dep.subject
        assert len(actor1.supplierDependency) == 1
        assert actor1.supplierDependency[0] is dep.subject
        assert len(actor2.clientDependency) == 1
        assert actor2.clientDependency[0] is dep.subject

        # Do the same thing, but now on a new diagram:

        diagram2 = self.element_factory.create(UML.Diagram)
        actoritem3 = diagram2.create(items.ActorItem, subject=actor1)
        actoritem4 = diagram2.create(items.ActorItem, subject=actor2)
        dep2 = diagram2.create(items.DependencyItem)

        adapter = component.queryMultiAdapter((actoritem3, dep2), IConnect)

        adapter.connect(dep2.head)

        adapter = component.queryMultiAdapter((actoritem4, dep2), IConnect)

        adapter.connect(dep2.tail)

        assert dep2.subject
        assert len(actor1.supplierDependency) == 1
        assert actor1.supplierDependency[0] is dep.subject
        assert len(actor2.clientDependency) == 1
        assert actor2.clientDependency[0] is dep.subject

        assert dep.subject is dep2.subject

    def test_implementation(self):
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, UML.Class)
        iface = self.create(items.InterfaceItem, UML.Interface)

        adapter = component.queryMultiAdapter((clazz, impl), IConnect)

        adapter.connect(impl.head)

        # Should not be allowed to connect to anything but Interfaces

        assert impl.head.connected_to is None

        adapter.connect(impl.tail)
        assert impl.tail.connected_to is clazz
        assert impl.subject is None

        adapter = component.queryMultiAdapter((iface, impl), IConnect)

        adapter.connect(impl.head)
        
        assert impl.head.connected_to is iface
        assert impl.subject is not None
        assert impl.subject.contract[0] is iface.subject
        assert impl.subject.implementatingClassifier[0] is clazz.subject

    def test_generalization(self):
        gen = self.create(items.GeneralizationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail)

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head)

        assert gen.head.connected_to is c2
        assert gen.subject is not None
        assert gen.subject.general is c2.subject
        assert gen.subject.specific is c1.subject

    def test_extension(self):
        gen = self.create(items.ExtensionItem)
        c1 = self.create(items.ClassItem, UML.Stereotype)
        c2 = self.create(items.ClassItem, UML.Class)

        assert len(list(self.element_factory.select())) == 3

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail)

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head)

        assert gen.head.connected_to is c2
        assert gen.subject is not None
        
        assert len(list(self.element_factory.select())) == 6, len(list(self.element_factory.select()))

        adapter.disconnect(gen.head)

        assert len(list(self.element_factory.select())) == 3, list(self.element_factory.select())

    def test_association(self):
        gen = self.create(items.AssociationItem)
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)

        assert len(list(self.element_factory.select())) == 3

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail)

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head)

        assert gen.head.connected_to is c2
        assert gen.subject is not None
        
        # Diagram, Class x2, Property *2, Association, LiteralSpec *2
        assert len(list(self.element_factory.select())) == 8, list(self.element_factory.select())
        assert gen.head_end.subject is not None
        assert gen.tail_end.subject is not None
        assert gen.head_end._name_bounds.width == 10
        assert gen.tail_end._name_bounds.width == 10

        gen.head_end.subject.name = 'cheese'
        assert gen.head_end._name_bounds.width > 10, gen.head_end._name_bounds.width

        adapter.disconnect(gen.head)

        assert len(list(self.element_factory.select())) == 3, list(self.element_factory.select())

    def test_flow_activitynodes(self):
        flow = self.create(items.FlowItem)
        i1 = self.create(items.InitialNodeItem, UML.InitialNode)
        f1 = self.create(items.ActivityFinalNodeItem, UML.ActivityFinalNode)
        f2 = self.create(items.FlowFinalNodeItem, UML.FlowFinalNode)

        assert len(self.element_factory.lselect()) == 4

        # head may not connect to FinalNode

        adapter = component.queryMultiAdapter((f1, flow), IConnect)
        assert adapter
        adapter.connect(flow.head)
        assert flow.head.connected_to is None

        adapter.connect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is f1

        adapter.disconnect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is None

        adapter = component.queryMultiAdapter((f2, flow), IConnect)
        assert adapter
        adapter.connect(flow.head)
        assert flow.head.connected_to is None

        adapter.connect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is f2

        adapter.disconnect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is None

        # tail may not connect to InitialNode

        adapter = component.queryMultiAdapter((i1, flow), IConnect)
        assert adapter
        adapter.connect(flow.tail)
        assert flow.head.connected_to is None
        assert flow.tail.connected_to is None

        adapter.connect(flow.head)
        assert flow.tail.connected_to is None
        assert flow.head.connected_to is i1

    
    def test_flow_action(self):
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        o1 = self.create(items.ObjectNodeItem, UML.ObjectNode)

        # diagram, two actions and object node, flow has no subject
        assert len(self.element_factory.lselect()) == 4, self.element_factory.lselect()

        # Connect between two actions (ControlFlow)
        adapter = component.queryMultiAdapter((a1, flow), IConnect)
        assert adapter
        adapter.connect(flow.tail)

        assert flow.tail.connected_to is a1
        assert flow.subject is None

        adapter = component.queryMultiAdapter((a2, flow), IConnect)
        adapter.connect(flow.head)

        assert flow.head.connected_to is a2
        assert flow.tail.connected_to is a1
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ControlFlow)

        adapter.connect(flow.tail)

        assert flow.head.connected_to is a2
        assert flow.tail.connected_to is a2
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ControlFlow)

        # Connection between action and objectNode (ObjectFlow)

        adapter = component.queryMultiAdapter((o1, flow), IConnect)
        adapter.connect(flow.head)

        assert flow.head.connected_to is o1
        assert flow.tail.connected_to is a2
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ObjectFlow)

        adapter.disconnect(flow.head)

        assert flow.head.connected_to is None
        assert flow.tail.connected_to is a2
        assert flow.subject is None

    def test_flow_connect(self):
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        o1 = self.create(items.ObjectNodeItem, UML.ObjectNode)

        # diagram, two actions and object node, flows has no subjects
        assert len(self.element_factory.lselect()) == 4, self.element_factory.lselect()

        adapter = component.queryMultiAdapter((a1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.tail)
        assert flow1.tail.connected_to is a1
        assert not a1.subject.incoming, a1.subject.incoming

        # More than one edge may be connected to an action:

        adapter = component.queryMultiAdapter((a1, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.tail)
        assert flow1.tail.connected_to is a1
        assert flow2.tail.connected_to is a1

        adapter = component.queryMultiAdapter((a2, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.head)
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
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        flow4 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        a3 = self.create(items.ActionItem, UML.Action)
        a4 = self.create(items.ActionItem, UML.Action)
        f1 = self.create(itemClass, joinNodeClass)

        #assert len(self.element_factory.lselect()) == 6, self.element_factory.lselect()

        # Connect between two actions (ControlFlow)
        # Connecting line this:
        #        head  tail|--flow2-->[ a2 ]
        # [ a1 ] --flow1-->|
        #                  |--flow3-->[ a3 ]

        # First connect the Actions:

        adapter = component.queryMultiAdapter((a1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.head)

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.tail)

        adapter = component.queryMultiAdapter((a3, flow3), IConnect)
        assert adapter
        adapter.connect(flow3.tail)

        # Now connect to ForkNode:

        adapter = component.queryMultiAdapter((f1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.tail)
        assert flow1.tail.connected_to is f1
        assert flow1.subject
        assert flow1.subject.target is f1.subject
        assert flow1.subject in f1.subject.incoming
        assert type(f1.subject) is joinNodeClass

        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.head)
        assert flow2.head.connected_to is f1
        assert flow2.subject.source is f1.subject
        assert flow2.subject in f1.subject.outgoing
        assert type(f1.subject) is joinNodeClass
        assert flow2.canvas

        adapter = component.queryMultiAdapter((f1, flow3), IConnect)
        assert adapter
        adapter.connect(flow3.head)
        assert flow3.head.connected_to is f1
        assert flow3.subject.source is f1.subject
        assert flow3.subject in f1.subject.outgoing
        assert len(f1.subject.outgoing) == 2

        assert type(f1.subject) is forkNodeClass, f1.subject

        # flow4 will force the forknode to become a combined node:

        adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        assert adapter
        adapter.connect(flow4.tail)
        assert type(f1.subject) is forkNodeClass

        adapter = component.queryMultiAdapter((a4, flow4), IConnect)
        adapter.connect(flow4.head)
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
        #adapter.connect(flow4.head)
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
        adapter.connect(flow2.tail)
        assert flow2.tail.connected_to is None, flow2.tail.connected_to

        adapter.disconnect(flow2.head)
        assert len(f1.subject.incoming) == 1, len(f1.subject.incoming)
        assert len(f1.subject.outgoing) == 0, len(f1.subject.outgoing)

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        adapter.connect(flow2.head)
        assert len(a2.subject.outgoing) == 0

        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        adapter.connect(flow2.tail)
        assert len(a2.subject.outgoing) == 1
        assert len(f1.subject.incoming) == 2
        assert len(f1.subject.outgoing) == 0, len(f1.subject.outgoing)
        assert type(f1.subject) is joinNodeClass, f1.subject

        # And of course I can't add another outgoing edge:
        #adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        #assert adapter
        #adapter.connect(flow4.head)
        #assert flow4.head.connected_to is None


    def test_flow_decision_merge(self):
        """
        Decision/Merge node is basically the same as Fork/Join node.
        """
        self.test_flow_fork_decision(itemClass=items.DecisionNodeItem,
                                     forkNodeClass=UML.DecisionNode,
                                     joinNodeClass=UML.MergeNode)


    def test_message_connect_lost(self):
        """Test lost message creating
        """
        factory = self.element_factory
        lifeline = self.create(items.LifelineItem)
        message = self.create(items.MessageItem)

        assert message.subject is None

        adapter = component.queryMultiAdapter((lifeline, message), IConnect)

        assert adapter is not None
        
        # connect tail of message to lifeline.
        adapter.connect(message.head)

        # If one side is connected a "lost" message is created
        assert message.subject is not None
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 1
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 1
        assert factory.lselect(lambda e: e.isKindOf(UML.Message))[0] is message.subject
        assert factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))[0] is message.subject.sendEvent
        
        adapter.disconnect(message.head)
        assert message.subject is None
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 0, \
                factory.lselect(lambda e: e.isKindOf(UML.Message))


    def test_message_connect(self):
        """Test message connection (not lost, not found)
        """
        factory = self.element_factory

        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        message = self.create(items.MessageItem)
        assert message.subject is None

        adapter = component.queryMultiAdapter((lifeline1, message), IConnect)
        assert adapter is not None
        
        # connect tail of message to lifeline.
        adapter.connect(message.head)

        # If one side is connected a "lost" message is created
        assert message.subject is not None
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 1
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 1
        assert factory.lselect(lambda e: e.isKindOf(UML.Message))[0] is message.subject
        assert factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))[0] is message.subject.sendEvent
        
        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail)
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 1
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 2
        assert factory.lselect(lambda e: e.isKindOf(UML.Message))[0] is message.subject
        assert message.subject.sendEvent in factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))
        assert message.subject.receiveEvent in factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))
        
        adapter = component.queryMultiAdapter((lifeline1, message), IConnect)
        adapter.disconnect(message.head)
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 1
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 1
        
        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        adapter.disconnect(message.tail)

        assert message.subject is None
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 0, \
                factory.lselect(lambda e: e.isKindOf(UML.Message))
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 0, \
                factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))


    def test_message_connect_cd(self):
        """Test connecting message on communication diagram
        """
        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        # make second lifeline to be on sequence diagram
        lifetime = lifeline2.lifetime
        lifetime.bottom.y += 10
        assert lifetime.is_visible

        message = self.create(items.MessageItem)
        assert message.subject is None

        adapter = component.queryMultiAdapter((lifeline1, message), IConnect)
        assert adapter is not None
        
        # connect head of message to lifeline
        adapter.connect(message.head)

        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail)
        # we should not be connected to second lifeline as it is on
        # sequence diagram
        assert message.tail.connected_to is None

        # make lifetime invisible and connect again
        lifetime.bottom.y -= 10
        assert not lifetime.is_visible

        adapter.connect(message.tail)
        assert message.tail.connected_to is lifeline2


    def test_message_connect_sd(self):
        """Test connecting message on sequence diagram
        """
        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        # make first lifeline to be on sequence diagram
        lifetime = lifeline1.lifetime
        lifetime.bottom.y += 10
        assert lifetime.is_visible

        message = self.create(items.MessageItem)
        assert message.subject is None

        adapter = component.queryMultiAdapter((lifeline1, message), IConnect)
        assert adapter is not None
        
        # connect head of message to lifeline
        adapter.connect(message.head)

        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail)
        # we should not be connected to second lifeline as it is on
        # communication diagram
        assert message.tail.connected_to is None

        # make second lifeline to be on sequence diagram
        lifetime = lifeline2.lifetime
        lifetime.bottom.y += 10
        assert lifetime.is_visible
        
        # connect again
        adapter.connect(message.tail)
        assert message.tail.connected_to is lifeline2


    def test_messages_disconnect_cd(self):
        """Test disconnecting messages on communication diagram
        """
        factory = self.element_factory

        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        message = self.create(items.MessageItem)
        assert message.subject is None

        adapter = component.queryMultiAdapter((lifeline1, message), IConnect)
        assert adapter is not None
        
        # connect head of message to lifeline
        adapter.connect(message.head)

        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail)
        assert message.tail.connected_to is lifeline2
        
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 1
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 2
        assert factory.lselect(lambda e: e.isKindOf(UML.Message))[0] is message.subject
        assert message.subject.sendEvent in factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))
        assert message.subject.receiveEvent in factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))

        subject = message.subject

        # add some more messages
        m1 = factory.create(UML.Message)
        m1.sendEvent = subject.sendEvent
        m1.receiveEvent = subject.receiveEvent

        m2 = factory.create(UML.Message)
        m2.sendEvent = subject.sendEvent
        m2.receiveEvent = subject.receiveEvent

        message.add_message(m1, False)
        message.add_message(m2, False)

        # add some inverted messages
        m3 = factory.create(UML.Message)
        m3.sendEvent = subject.receiveEvent
        m3.receiveEvent = subject.sendEvent

        m4 = factory.create(UML.Message)
        m4.sendEvent = subject.receiveEvent
        m4.receiveEvent = subject.sendEvent

        message.add_message(m3, True)
        message.add_message(m4, True)

        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 5

        # disconnect
        adapter.disconnect(message.head)
        adapter.disconnect(message.tail)

        # we expect no messages
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 0


# vim:sw=4:et:ai
