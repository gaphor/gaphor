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


    def test_lifetime_connection(self):
        """Test messages' lifetimes connection
        """
        message = self.create(items.MessageItem)
        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        # make lifelines to be in sequence diagram mode
        lifeline1.lifetime.bottom.y += 10
        lifeline2.lifetime.bottom.y += 10
        assert lifeline1.lifetime.is_visible and lifeline2.lifetime.is_visible

        # connect lifetimes with messages message to lifeline's head
        self.connect(message, message.head, lifeline1, lifeline1._lifetime_port)
        self.connect(message, message.tail, lifeline2, lifeline2._lifetime_port)

        self.assertTrue(message.subject is not None)
        self.assertEquals(message.subject.messageKind, 'complete')


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



class DiagramModeMessageConnectionTestCase(TestCase):
    def test_message_glue_cd(self):
        """Test glueing message on communication diagram
        """
        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        # make second lifeline to be in sequence diagram mode
        lifetime = lifeline2.lifetime
        lifetime.bottom.y += 10
        assert lifetime.is_visible

        message = self.create(items.MessageItem)

        # connect head of message to lifeline's head
        self.connect(message, message.head, lifeline1)

        glued = self.glue(message, message.tail, lifeline2, lifeline2._lifetime_port)
        # no connection possible as 2nd lifeline is in sequence diagram
        # mode
        self.assertFalse(glued)


    def test_message_glue_sd(self):
        """Test glueing message on sequence diagram
        """
        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)

        # make 2nd lifeline to be in sequence diagram mode
        lifetime = lifeline2.lifetime
        lifetime.bottom.y += 10
        assert lifetime.is_visible

        message = self.create(items.MessageItem)

        # connect lifetime of message to lifeline's lifetime
        self.connect(message, message.head, lifeline1, lifeline1._lifetime_port)

        glued = self.glue(message, message.tail, lifeline2)
        # no connection possible as 2nd lifeline is in communication
        # diagram mode
        self.assertFalse(glued)


    def test_messages_disconnect_cd(self):
        """Test disconnecting messages on communication diagram
        """
        lifeline1 = self.create(items.LifelineItem)
        lifeline2 = self.create(items.LifelineItem)
        message = self.create(items.MessageItem)

        self.connect(message, message.head, lifeline1)
        self.connect(message, message.tail, lifeline2)
        
        factory = self.element_factory
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

        assert len(self.kindof(UML.Message)) == 5

        # disconnect
        self.disconnect(message, message.head)
        self.disconnect(message, message.tail)

        # we expect no messages
        self.assertEquals(0, len(self.kindof(UML.Message)))


# vim:sw=4:et:ai
