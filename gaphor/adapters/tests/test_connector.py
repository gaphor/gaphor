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

    def test_extension(self):
        gen = self.create(items.ExtensionItem)
        c1 = self.create(items.ClassItem, UML.Stereotype)
        c2 = self.create(items.ClassItem, UML.Class)

        assert len(list(self.element_factory.select())) == 3

        adapter = component.queryMultiAdapter((c1, gen), IConnect)

        adapter.connect(gen.tail, c1.ports()[0])

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head, c2.ports()[0])

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

        adapter.connect(gen.tail, c1.ports()[-1])

        assert gen.tail.connected_to is c1
        assert gen.subject is None

        adapter = component.queryMultiAdapter((c2, gen), IConnect)

        adapter.connect(gen.head, c2.ports()[0])

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
        adapter.connect(flow.head, f1.ports()[0])
        assert flow.head.connected_to is None

        adapter.connect(flow.tail, f1.ports()[0])
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
        adapter.connect(flow.tail, a1.ports()[0])

        assert flow.tail.connected_to is a1
        assert flow.subject is None

        adapter = component.queryMultiAdapter((a2, flow), IConnect)
        adapter.connect(flow.head, a2.ports()[0])

        assert flow.head.connected_to is a2
        assert flow.tail.connected_to is a1
        assert not flow.subject is None
        assert isinstance(flow.subject, UML.ControlFlow)

        adapter.connect(flow.tail, a2.ports()[0])

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
        adapter.connect(flow1.tail, a1.ports()[0])
        assert flow1.tail.connected_to is a1
        assert not a1.subject.incoming, a1.subject.incoming

        # More than one edge may be connected to an action:

        adapter = component.queryMultiAdapter((a1, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.tail, a1.ports()[0])
        assert flow1.tail.connected_to is a1
        assert flow2.tail.connected_to is a1

        adapter = component.queryMultiAdapter((a2, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.head, a2.ports()[0])
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
        adapter.connect(flow1.head, a1.ports()[0])

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.tail, a2.ports()[0])

        adapter = component.queryMultiAdapter((a3, flow3), IConnect)
        assert adapter
        adapter.connect(flow3.tail, a3.ports()[0])

        # Now connect to ForkNode:

        adapter = component.queryMultiAdapter((f1, flow1), IConnect)
        assert adapter
        adapter.connect(flow1.tail, f1.ports()[0])
        assert flow1.tail.connected_to is f1
        assert flow1.subject
        assert flow1.subject.target is f1.subject
        assert flow1.subject in f1.subject.incoming
        assert type(f1.subject) is joinNodeClass

        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        assert adapter
        adapter.connect(flow2.head, f1.ports()[0])
        assert flow2.head.connected_to is f1
        assert flow2.subject.source is f1.subject
        assert flow2.subject in f1.subject.outgoing
        assert type(f1.subject) is joinNodeClass
        assert flow2.canvas

        adapter = component.queryMultiAdapter((f1, flow3), IConnect)
        assert adapter
        adapter.connect(flow3.head, f1.ports()[0])
        assert flow3.head.connected_to is f1
        assert flow3.subject.source is f1.subject
        assert flow3.subject in f1.subject.outgoing
        assert len(f1.subject.outgoing) == 2

        assert type(f1.subject) is forkNodeClass, f1.subject

        # flow4 will force the forknode to become a combined node:
        # Connecting line this:
        #        head  tail|--flow2-->[ a2 ]
        # [ a1 ] --flow1-->|
        # [ a4 ] --flow4-->|--flow3-->[ a3 ]

        adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        assert adapter
        adapter.connect(flow4.tail, f1.ports()[0])
        assert type(f1.subject) is forkNodeClass

        adapter = component.queryMultiAdapter((a4, flow4), IConnect)
        adapter.connect(flow4.head, a4.ports()[0])
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
        #adapter.connect(flow4.head, f1.ports()[0])
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
        adapter.connect(flow2.tail, f1.ports()[0])
        assert flow2.tail.connected_to is None, flow2.tail.connected_to

        adapter.disconnect(flow2.head, f1.ports()[0])
        assert len(f1.subject.incoming) == 1, len(f1.subject.incoming)
        assert len(f1.subject.outgoing) == 0, len(f1.subject.outgoing)

        adapter = component.queryMultiAdapter((a2, flow2), IConnect)
        adapter.connect(flow2.head, f1.ports()[0])
        assert len(a2.subject.outgoing) == 0

        adapter = component.queryMultiAdapter((f1, flow2), IConnect)
        adapter.connect(flow2.tail, f1.ports()[0])
        assert len(a2.subject.outgoing) == 1
        assert len(f1.subject.incoming) == 2
        assert len(f1.subject.outgoing) == 0, len(f1.subject.outgoing)
        assert type(f1.subject) is joinNodeClass, f1.subject

        # And of course I can't add another outgoing edge:
        #adapter = component.queryMultiAdapter((f1, flow4), IConnect)
        #assert adapter
        #adapter.connect(flow4.head, f1.ports()[0])
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
        adapter.connect(message.head, lifeline.ports()[0])

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
        adapter.connect(message.head, lifeline1.ports()[0])

        # If one side is connected a "lost" message is created
        assert message.subject is not None
        assert len(factory.lselect(lambda e: e.isKindOf(UML.Message))) == 1
        assert len(factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))) == 1
        assert factory.lselect(lambda e: e.isKindOf(UML.Message))[0] is message.subject
        assert factory.lselect(lambda e: e.isKindOf(UML.EventOccurrence))[0] is message.subject.sendEvent
        
        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail, lifeline2.ports()[0])
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
        adapter.connect(message.head, lifeline1.ports()[0])

        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail, lifeline2.ports()[0])
        # we should not be connected to second lifeline as it is on
        # sequence diagram
        assert message.tail.connected_to is None

        # make lifetime invisible and connect again
        lifetime.bottom.y -= 10
        assert not lifetime.is_visible

        adapter.connect(message.tail, lifeline2.ports()[0])
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
        adapter.connect(message.head, lifeline1.ports()[0])

        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail, lifeline2.ports()[0])
        # we should not be connected to second lifeline as it is on
        # communication diagram
        assert message.tail.connected_to is None

        # make second lifeline to be on sequence diagram
        lifetime = lifeline2.lifetime
        lifetime.bottom.y += 10
        assert lifetime.is_visible
        
        # connect again
        adapter.connect(message.tail, lifeline2.ports()[0])
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
        adapter.connect(message.head, lifeline1.ports()[0])

        adapter = component.queryMultiAdapter((lifeline2, message), IConnect)
        assert adapter is not None

        adapter.connect(message.tail, lifeline2.ports()[0])
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
