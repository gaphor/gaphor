"""
Test messages.
"""

from gaphor import UML
from gaphor.UML.interactions.message import MessageItem


def test_message_persistence(diagram, element_factory, saver, loader):
    diagram.create(MessageItem, subject=element_factory.create(UML.Message))

    data = saver()
    loader(data)
    new_diagram = next(element_factory.select(UML.Diagram))
    item = new_diagram.canvas.select(MessageItem)[0]

    assert item
