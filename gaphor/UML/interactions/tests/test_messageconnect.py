"""Message connection adapter tests."""

import pytest

from gaphor import UML
from gaphor.diagram.group import group
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.interactions.executionspecification import ExecutionSpecificationItem
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.interactions.message import MessageItem


def test_head_glue(diagram):
    """Test message head glue."""
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    # get head port
    port = ll.ports()[0]
    glued = allow(msg, msg.head, ll, port)
    assert glued


def test_visible_lifetime_glue(diagram):
    """Test message to visible lifetime glue."""
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    ll.lifetime.visible = True

    glued = allow(msg, msg.head, ll, ll.lifetime.port)
    assert glued


def test_lost_message_connection(diagram, element_factory):
    """Test lost message connection."""
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll)

    messages = element_factory.lselect(UML.Message)
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # If one side is connected a "lost" message is created
    assert msg.subject is not None
    assert msg.subject.messageKind == "lost"

    assert len(messages) == 1
    assert len(occurrences) == 1
    assert messages[0] is msg.subject
    assert occurrences[0] is msg.subject.sendEvent


def test_found_message_connection(diagram, element_factory):
    """Test found message connection."""
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.tail, ll)

    messages = element_factory.lselect(UML.Message)
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # If one side is connected a "found" message is created
    assert msg.subject is not None
    assert msg.subject.messageKind == "found"

    assert len(messages) == 1
    assert len(occurrences) == 1
    assert messages[0] is msg.subject
    assert occurrences[0] is msg.subject.receiveEvent


def test_complete_message_connection(diagram, element_factory):
    """Test complete message connection."""
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll1)
    connect(msg, msg.tail, ll2)

    messages = element_factory.lselect(UML.Message)
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # two sides are connected - "complete" message is created
    assert msg.subject is not None
    assert msg.subject.messageKind == "complete"

    assert len(messages) == 1
    assert len(occurrences) == 2
    assert messages[0] is msg.subject
    assert msg.subject.sendEvent in occurrences, f"{occurrences}"
    assert msg.subject.receiveEvent in occurrences, f"{occurrences}"


def test_lifetime_connection(diagram):
    """Test messages' lifetimes connection."""
    msg = diagram.create(MessageItem)
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)

    # make lifelines to be in sequence diagram mode
    ll1.lifetime.visible = True
    ll2.lifetime.visible = True
    assert ll1.lifetime.visible and ll2.lifetime.visible

    # connect lifetimes with a message to the lifeline's head
    connect(msg, msg.head, ll1, ll1.lifetime.port)
    connect(msg, msg.tail, ll2, ll2.lifetime.port)

    assert msg.subject is not None
    assert msg.subject.messageKind == "complete"


def test_lifetime_connect_disconnect(diagram):
    """Test messages' lifetimes connection."""
    msg = diagram.create(MessageItem)
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)

    # make lifelines to be in sequence diagram mode
    ll1.lifetime.visible = True
    ll2.lifetime.visible = True
    assert ll1.lifetime.visible and ll2.lifetime.visible

    # connect lifetimes with a message to the lifeline's head
    connect(msg, msg.head, ll1, ll1.lifetime.port)
    connect(msg, msg.tail, ll2, ll2.lifetime.port)
    disconnect(msg, msg.tail)

    assert msg.subject is not None
    assert msg.subject.messageKind == "lost"


@pytest.mark.parametrize("end_name", ["head", "tail"])
def test_message_is_owned_by_implicit_interaction_connecting_to_head(
    diagram, element_factory, end_name
):
    """Test messages' lifetimes connection."""
    interaction = element_factory.create(UML.Interaction)
    msg = diagram.create(MessageItem)
    ll = diagram.create(LifelineItem, subject=element_factory.create(UML.Lifeline))
    ll.subject.interaction = interaction

    connect(msg, getattr(msg, end_name), ll)

    assert msg.subject is not None
    assert msg.subject.interaction is interaction
    assert msg.parent is None


@pytest.mark.parametrize("end_name", ["head", "tail"])
def test_message_is_owned_by_interaction_item_connecting_to_one_end(
    diagram, element_factory, end_name
):
    """Test messages' lifetimes connection."""
    interaction = diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )
    ll = diagram.create(LifelineItem, subject=element_factory.create(UML.Lifeline))
    assert group(interaction.subject, ll.subject)

    msg = diagram.create(MessageItem)
    connect(msg, getattr(msg, end_name), ll)

    assert msg.subject is not None
    assert msg.subject.interaction is interaction.subject


def test_disconnection(diagram):
    """Test message disconnection."""
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll1)
    connect(msg, msg.tail, ll2)

    # one side disconnection
    disconnect(msg, msg.head)
    assert msg.subject is not None, f"{msg.subject}"

    # 2nd side disconnection
    disconnect(msg, msg.tail)
    assert msg.subject is None, f"{msg.subject}"


def test_communication_diagram_message_head_glue(diagram):
    communication = diagram.create(LifelineItem)
    sequence = diagram.create(LifelineItem)
    sequence.lifetime.visible = True
    message = diagram.create(MessageItem)

    connect(message, message.tail, sequence)

    assert allow(message, message.head, communication, communication.lifetime.port)


def test_communication_diagram_message_tail_glue(diagram):
    lifeline1 = diagram.create(LifelineItem)
    lifeline2 = diagram.create(LifelineItem)
    message = diagram.create(MessageItem)

    lifeline2.lifetime.visible = True
    connect(message, message.head, lifeline1)

    assert allow(message, message.tail, lifeline2, lifeline2.lifetime.port)


def test_message_glue_from_lifetimee_to_head(diagram):
    """Test gluing message on communication diagram."""

    lifeline1 = diagram.create(LifelineItem)
    lifeline2 = diagram.create(LifelineItem)
    message = diagram.create(MessageItem)

    lifeline1.lifetime.visible = True

    # connect head of message to lifeline's head
    connect(message, message.head, lifeline1)

    assert allow(message, message.tail, lifeline2, lifeline2.lifetime.port)


def test_messages_disconnect_cd(diagram, element_factory):
    """Test disconnecting messages on communication diagram."""
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll1)
    connect(msg, msg.tail, ll2)

    subject = msg.subject

    assert subject.sendEvent
    assert subject.receiveEvent

    messages = element_factory.lselect(UML.Message)
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # verify integrity of messages
    assert len(messages) == 1
    assert len(occurrences) == 2


def test_message_connect_to_execution_specification(diagram, element_factory):
    """Test gluing message on sequence diagram."""

    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    exec_spec = diagram.create(ExecutionSpecificationItem)
    message = diagram.create(MessageItem)
    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)

    connect(message, message.head, exec_spec, exec_spec.ports()[0])

    assert message.subject
    assert message.subject.sendEvent.covered is lifeline.subject


def test_message_connect_to_execution_specification_in_interaction(
    diagram, element_factory
):
    interaction = diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )

    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    assert group(interaction.subject, lifeline.subject)

    exec_spec = diagram.create(ExecutionSpecificationItem)
    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)

    message = diagram.create(MessageItem)
    connect(message, message.head, exec_spec, exec_spec.ports()[0])

    # In this particular case, the message is not (yet) tied to an interaction
    message.subject.interaction = None

    connect(message, message.tail, lifeline, lifeline.lifetime.port)

    assert lifeline.subject.interaction is interaction.subject
    assert exec_spec.subject.enclosingInteraction is interaction.subject
    assert message.subject.interaction is interaction.subject


def test_message_disconnect_from_execution_specification(
    diagram, element_factory, sanitizer_service
):
    """Test gluing message on sequence diagram."""

    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    exec_spec = diagram.create(ExecutionSpecificationItem)
    message = diagram.create(MessageItem)
    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)
    connect(message, message.head, exec_spec, exec_spec.ports()[0])

    disconnect(message, message.head)

    messages = element_factory.lselect(UML.Message)
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    assert not message.subject
    assert not len(messages)
    assert not len(occurrences)
