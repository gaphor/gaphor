"""Test messages."""

from gaphor import UML
from gaphor.diagram.grouping import Group
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.message import MessageItem


def test_message_persistence(diagram, element_factory, saver, loader):
    diagram.create(MessageItem, subject=element_factory.create(UML.Message))

    data = saver()
    loader(data)
    new_diagram = next(element_factory.select(UML.Diagram))
    item = next(new_diagram.select(MessageItem))

    assert item


def test_group_message_item_without_subject(diagram, element_factory):
    interaction = diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )
    message = diagram.create(MessageItem)

    Group(interaction, message).group()

    assert message.subject is None


def test_group_message_item_with_subject(diagram, element_factory):
    interaction = diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )
    message = diagram.create(MessageItem, subject=element_factory.create(UML.Message))

    Group(interaction, message).group()

    assert message.subject
    assert message.subject.interaction is interaction.subject
