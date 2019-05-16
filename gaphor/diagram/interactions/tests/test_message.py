"""
Test messages.
"""

from gaphor import UML
from gaphor.diagram.interactions.message import MessageItem
from gaphor.tests.testcase import TestCase


class MessageTestCase(TestCase):
    def test_message(self):
        """Test creation of messages
        """
        self.create(MessageItem, UML.Message)

    def test_adding_message(self):
        """Test adding message on communication diagram
        """
        factory = self.element_factory
        item = self.create(MessageItem, UML.Message)

        message = factory.create(UML.Message)
        message.name = "test-message"

        item.add_message(message, False)
        self.assertTrue(message in item._messages)
        self.assertTrue(message not in item._inverted_messages)
        self.assertEqual(item._messages[message].text, "test-message")

        message = factory.create(UML.Message)
        message.name = "test-inverted-message"
        item.add_message(message, True)
        self.assertTrue(message in item._inverted_messages)
        self.assertTrue(message not in item._messages)
        self.assertEqual(item._inverted_messages[message].text, "test-inverted-message")

    def test_changing_message_text(self):
        """Test changing message text
        """
        factory = self.element_factory
        item = self.create(MessageItem, UML.Message)

        message = factory.create(UML.Message)
        message.name = "test-message"
        item.add_message(message, False)
        self.assertEqual(item._messages[message].text, "test-message")

        item.set_message_text(message, "test-message-changed", False)
        self.assertEqual(item._messages[message].text, "test-message-changed")

        message = factory.create(UML.Message)
        message.name = "test-message"
        item.add_message(message, True)
        self.assertEqual(item._inverted_messages[message].text, "test-message")

        item.set_message_text(message, "test-message-changed", True)
        self.assertEqual(item._inverted_messages[message].text, "test-message-changed")

    def test_message_removal(self):
        """Test message removal
        """
        factory = self.element_factory
        item = self.create(MessageItem, UML.Message)

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
        factory = self.element_factory
        item = self.create(MessageItem, UML.Message)

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
        factory = self.element_factory
        item = self.create(MessageItem, UML.Message)

        m1 = factory.create(UML.Message)
        m2 = factory.create(UML.Message)
        m3 = factory.create(UML.Message)
        m4 = factory.create(UML.Message)
        m1.name = "m1"
        m2.name = "m2"
        m3.name = "m3"
        m4.name = "m4"

        item.add_message(m1, False)
        item.add_message(m2, False)
        item.add_message(m3, True)
        item.add_message(m4, True)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, MessageItem))[0]
        self.assertEqual(len(item._messages), 2)
        self.assertEqual(len(item._inverted_messages), 2)
        # check for loaded messages and order of messages
        self.assertEqual(["m1", "m2"], [m.name for m in item._messages])
        self.assertEqual(["m3", "m4"], [m.name for m in item._inverted_messages])
