"""
Test messages.
"""

from gaphor import UML
from gaphor.diagram.interactions.message import MessageItem
from gaphor.tests.testcase import TestCase


class MessageTestCase(TestCase):
    def test_message_persistence(self):
        """Test message saving/loading
        """
        self.create(MessageItem, UML.Message)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, MessageItem))[0]

        assert item
