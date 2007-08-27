"""
Test messages.
"""

import unittest
from cStringIO import StringIO

from gaphor import UML
from gaphor.diagram.message import MessageItem
from gaphor import storage
from gaphor.misc.xmlwriter import XMLWriter


class MessageTestCase(unittest.TestCase):
    def test_message(self):
        """Test creation of messages
        """
        factory = UML.ElementFactory()
        diagram = factory.create(UML.Diagram)
        item = diagram.create(MessageItem, subject=factory.create(UML.Message))

        diagram.canvas.update()


    def test_adding_message(self):
        """Test adding message on communication diagram
        """
        factory = UML.ElementFactory()
        diagram = factory.create(UML.Diagram)
        item = diagram.create(MessageItem, subject=factory.create(UML.Message))

        diagram.canvas.update()

        message = factory.create(UML.Message)
        message.name = 'test-message'
        item.add_message(message, False)
        self.assertTrue(message in item._messages)
        self.assertTrue(message not in item._inverted_messages)
        self.assertEquals(item._messages[message].text, 'test-message')


        message = factory.create(UML.Message)
        message.name = 'test-inverted-message'
        item.add_message(message, True)
        self.assertTrue(message in item._inverted_messages)
        self.assertTrue(message not in item._messages)
        self.assertEquals(item._inverted_messages[message].text, 'test-inverted-message')


    def test_changing_message_text(self):
        """Test changing message text
        """
        factory = UML.ElementFactory()
        diagram = factory.create(UML.Diagram)
        item = diagram.create(MessageItem, subject=factory.create(UML.Message))

        diagram.canvas.update()

        message = factory.create(UML.Message)
        message.name = 'test-message'
        item.add_message(message, False)
        self.assertEquals(item._messages[message].text, 'test-message')

        item.set_message_text(message, 'test-message-changed', False)
        self.assertEquals(item._messages[message].text, 'test-message-changed')

        message = factory.create(UML.Message)
        message.name = 'test-message'
        item.add_message(message, True)
        self.assertEquals(item._inverted_messages[message].text, 'test-message')

        item.set_message_text(message, 'test-message-changed', True)
        self.assertEquals(item._inverted_messages[message].text, 'test-message-changed')


    def test_message_removal(self):
        """Test message removal
        """
        factory = UML.ElementFactory()
        diagram = factory.create(UML.Diagram)
        item = diagram.create(MessageItem, subject=factory.create(UML.Message))

        diagram.canvas.update()

        message = factory.create(UML.Message)
        item.add_message(message, False)
        self.assertTrue(message in item._messages)

        item.remove_message(message, False)
        self.assertTrue(message not in item._messages)

        message = factory.create(UML.Message)
        item.add_message(message, True)
        self.assertTrue(message in item._inverted_messages)

        item.remove_message(message, True)
        self.assertTrue(message not in item._inverted_messages)


    def test_messages_swapping(self):
        """Test messages swapping
        """
        factory = UML.ElementFactory()
        diagram = factory.create(UML.Diagram)
        item = diagram.create(MessageItem, subject=factory.create(UML.Message))

        diagram.canvas.update()

        m1 = factory.create(UML.Message)
        m2 = factory.create(UML.Message)
        item.add_message(m1, False)
        item.add_message(m2, False)
        item.swap_messages(m1, m2, False)

        m1 = factory.create(UML.Message)
        m2 = factory.create(UML.Message)
        item.add_message(m1, True)
        item.add_message(m2, True)
        item.swap_messages(m1, m2, True)


    def test_message_persistence(self):
        """Test message saving/loading
        """
        factory = UML.ElementFactory()
        diagram = factory.create(UML.Diagram)
        item = diagram.create(MessageItem, subject=factory.create(UML.Message))

        diagram.canvas.update()

        m1 = factory.create(UML.Message)
        m2 = factory.create(UML.Message)
        m3 = factory.create(UML.Message)
        m4 = factory.create(UML.Message)
        m1.name = 'm1'
        m2.name = 'm2'
        m3.name = 'm3'
        m4.name = 'm4'

        item.add_message(m1, False)
        item.add_message(m2, False)
        item.add_message(m3, True)
        item.add_message(m4, True)

        # save
        f = StringIO()
        storage.save(XMLWriter(f), factory=factory)
        data = f.getvalue()
        f.close()

        # load
        factory = UML.ElementFactory()
        assert not list(factory.select())

        f = StringIO(data)
        storage.load(f, factory=factory)
        f.close()
        
        diagram = factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        item = diagram.canvas.select(lambda e: isinstance(e, MessageItem))[0]
        self.assertEquals(len(item._messages), 2)
        self.assertEquals(len(item._inverted_messages), 2)
