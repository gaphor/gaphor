"""
Message connection adapter tests.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items

class BasicMessageConnectionsTestCase(TestCase):
    def test_head_glue(self):
        """Test message head glue
        """
        ll = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        # get head port
        port = ll.ports()[0]
        glued = self.glue(msg, msg.head, ll, port)
        self.assertTrue(glued)


    def test_invisible_lifetime_glue(self):
        """Test message invisible lifetime glue
        """
        ll = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        # get lifetime port
        port = ll._lifetime_port
        glued = self.glue(msg, msg.head, ll, port)
        assert not ll.lifetime.is_visible
        self.assertFalse(glued)


    def test_visible_lifetime_glue(self):
        """Test message invisible lifetime glue
        """
        ll = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        ll.lifetime.bottom.y += 10

        # get lifetime port
        port = ll._lifetime_port
        glued = self.glue(msg, msg.head, ll, port)

        assert ll.lifetime.is_visible
        self.assertTrue(glued)


    def test_lost_message_connection(self):
        """Test lost message connection
        """
        ll = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        self.connect(msg, msg.head, ll)

        # If one side is connected a "lost" message is created
        self.assertTrue(msg.subject is not None)
        self.assertEquals(msg.subject.messageKind, 'lost')

        messages = self.kindof(UML.Message)
        occurences = self.kindof(UML.EventOccurrence)

        self.assertEquals(1, len(messages))
        self.assertEquals(1, len(occurences))
        self.assertTrue(messages[0] is msg.subject)
        self.assertTrue(occurences[0] is msg.subject.sendEvent)
        

    def test_found_message_connection(self):
        """Test found message connection
        """
        ll = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        self.connect(msg, msg.tail, ll)

        # If one side is connected a "found" message is created
        self.assertTrue(msg.subject is not None)
        self.assertEquals(msg.subject.messageKind, 'found')

        messages = self.kindof(UML.Message)
        occurences = self.kindof(UML.EventOccurrence)

        self.assertEquals(1, len(messages))
        self.assertEquals(1, len(occurences))
        self.assertTrue(messages[0] is msg.subject)
        self.assertTrue(occurences[0] is msg.subject.receiveEvent)
        

    def test_complete_message_connection(self):
        """Test complete message connection
        """
        ll1 = self.create(items.LifelineItem)
        ll2 = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        self.connect(msg, msg.head, ll1)
        self.connect(msg, msg.tail, ll2)

        # two sides are connected - "complete" message is created
        self.assertTrue(msg.subject is not None)
        self.assertEquals(msg.subject.messageKind, 'complete')

        messages = self.kindof(UML.Message)
        occurences = self.kindof(UML.EventOccurrence)

        self.assertEquals(1, len(messages))
        self.assertEquals(2, len(occurences))
        self.assertTrue(messages[0] is msg.subject)
        self.assertTrue(msg.subject.sendEvent in occurences, '%s' % occurences)
        self.assertTrue(msg.subject.receiveEvent in occurences, '%s' % occurences)


    def test_disconnection(self):
        """Test message disconnection
        """
        ll1 = self.create(items.LifelineItem)
        ll2 = self.create(items.LifelineItem)
        msg = self.create(items.MessageItem)

        self.connect(msg, msg.head, ll1)
        self.connect(msg, msg.tail, ll2)

        # one side disconnection
        self.disconnect(msg, msg.head)
        self.assertTrue(msg.subject is not None, '%s' % msg.subject)

        # 2nd side disconnection
        self.disconnect(msg, msg.tail)
        self.assertTrue(msg.subject is None, '%s' % msg.subject)



class CommunicationDiagramMessageConnectionsTestCase(TestCase):
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


class SequenceDiagramMessageConnectionsTestCase(TestCase):
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



# vim:sw=4:et:ai
