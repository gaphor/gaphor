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
