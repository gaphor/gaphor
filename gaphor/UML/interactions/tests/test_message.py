"""Test messages."""
import pytest
from gaphas.item import SE

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.group import group
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.interactions.message import MessageItem


def test_message_persistence(diagram, element_factory, saver, loader):
    diagram.create(MessageItem, subject=element_factory.create(UML.Message))

    data = saver()
    loader(data)
    new_diagram = next(element_factory.select(Diagram))
    item = next(new_diagram.select(MessageItem))

    assert item


def test_group_message_item_without_subject(diagram, element_factory):
    interaction = diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )
    message = diagram.create(MessageItem)

    with pytest.raises(TypeError):
        group(interaction.subject, message.subject)

    assert message.subject is None


def test_group_message_item_with_subject(diagram, element_factory):
    interaction = diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )
    message = diagram.create(MessageItem, subject=element_factory.create(UML.Message))

    group(interaction.subject, message.subject)

    assert message.subject
    assert message.subject.interaction is interaction.subject


def test_message_connected_to_lifeline(diagram, element_factory, saver, loader):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.length = 100
    message = diagram.create(MessageItem, subject=element_factory.create(UML.Message))
    diagram.update({lifeline, message})
    message.head.pos.x = lifeline.handles()[SE].pos.x
    message.head.pos.y = lifeline.handles()[-1].pos.y

    connect(message, message.head, lifeline)
    assert lifeline.lifetime.visible
    assert (
        diagram.connections.get_connection(message.head).port is lifeline.lifetime.port
    )

    data = saver()
    loader(data)

    new_diagram = next(element_factory.select(Diagram))
    new_lifeline = next(new_diagram.select(LifelineItem))
    new_message = next(new_diagram.select(MessageItem))
    new_port = new_diagram.connections.get_connection(new_message.head).port

    assert new_lifeline.lifetime.visible
    assert new_lifeline.lifetime.length == 100
    assert new_port is new_lifeline.lifetime.port
