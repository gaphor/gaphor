"""
Message connection adapter tests.
"""

from gaphor import UML
from gaphor.diagram.interactions.executionspecification import (
    ExecutionSpecificationItem,
)
from gaphor.diagram.interactions.lifeline import LifelineItem
from gaphor.diagram.interactions.message import MessageItem
from gaphor.diagram.tests.fixtures import allow, connect, disconnect


def test_head_glue(diagram):
    """Test message head glue
    """
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    # get head port
    port = ll.ports()[0]
    glued = allow(msg, msg.head, ll, port)
    assert glued


def test_invisible_lifetime_glue(diagram):
    """Test message to invisible lifetime glue
    """
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    glued = allow(msg, msg.head, ll, ll.lifetime.port)

    assert not ll.lifetime.visible
    assert not glued


def test_visible_lifetime_glue(diagram):
    """Test message to visible lifetime glue
    """
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    ll.lifetime.visible = True

    glued = allow(msg, msg.head, ll, ll.lifetime.port)
    assert glued


def test_lost_message_connection(diagram, element_factory):
    """Test lost message connection
    """
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll)

    messages = element_factory.lselect(lambda e: e.isKindOf(UML.Message))
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # If one side is connected a "lost" message is created
    assert msg.subject is not None
    assert msg.subject.messageKind == "lost"

    assert 1 == len(messages)
    assert 1 == len(occurrences)
    assert messages[0] is msg.subject
    assert occurrences[0] is msg.subject.sendEvent


def test_found_message_connection(diagram, element_factory):
    """Test found message connection
    """
    ll = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.tail, ll)

    messages = element_factory.lselect(lambda e: e.isKindOf(UML.Message))
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # If one side is connected a "found" message is created
    assert msg.subject is not None
    assert msg.subject.messageKind == "found"

    assert 1 == len(messages)
    assert 1 == len(occurrences)
    assert messages[0] is msg.subject
    assert occurrences[0] is msg.subject.receiveEvent


def test_complete_message_connection(diagram, element_factory):
    """Test complete message connection
    """
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll1)
    connect(msg, msg.tail, ll2)

    messages = element_factory.lselect(lambda e: e.isKindOf(UML.Message))
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # two sides are connected - "complete" message is created
    assert msg.subject is not None
    assert msg.subject.messageKind == "complete"

    assert 1 == len(messages)
    assert 2 == len(occurrences)
    assert messages[0] is msg.subject
    assert msg.subject.sendEvent in occurrences, f"{occurrences}"
    assert msg.subject.receiveEvent in occurrences, f"{occurrences}"


def test_lifetime_connection(diagram):
    """Test messages' lifetimes connection
    """
    msg = diagram.create(MessageItem)
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)

    # make lifelines to be in sequence diagram mode
    ll1.lifetime.visible = True
    ll2.lifetime.visible = True
    assert ll1.lifetime.visible and ll2.lifetime.visible

    # connect lifetimes with messages message to lifeline's head
    connect(msg, msg.head, ll1, ll1.lifetime.port)
    connect(msg, msg.tail, ll2, ll2.lifetime.port)

    assert msg.subject is not None
    assert msg.subject.messageKind == "complete"


def test_disconnection(diagram):
    """Test message disconnection
    """
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


def test_lifetime_connectivity_on_head(diagram, element_factory):
    """Test lifeline's lifetime connectivity change on head connection
    """
    ll = diagram.create(LifelineItem, subject=element_factory.create(UML.Lifeline))
    msg = diagram.create(MessageItem)

    # connect message to lifeline's head, lifeline's lifetime
    # visibility and connectivity should change
    connect(msg, msg.head, ll)
    assert not ll.lifetime.visible
    assert not ll.lifetime.connectable
    assert ll.lifetime.MIN_LENGTH == ll.lifetime.min_length

    # ... and disconnection
    disconnect(msg, msg.head)
    assert ll.lifetime.connectable
    assert ll.lifetime.MIN_LENGTH == ll.lifetime.min_length


def test_lifetime_connectivity_on_lifetime(diagram, element_factory):
    """Test lifeline's lifetime connectivity change on lifetime connection
    """
    ll = diagram.create(LifelineItem, subject=element_factory.create(UML.Lifeline))
    msg = diagram.create(MessageItem)

    ll.lifetime.visible = True

    # connect message to lifeline's lifetime, lifeline's lifetime
    # visibility and connectivity should be unchanged
    connect(msg, msg.head, ll, ll.lifetime.port)
    assert ll.lifetime.connectable
    assert ll.lifetime.MIN_LENGTH_VISIBLE == ll.lifetime.min_length

    # ... and disconnection
    disconnect(msg, msg.head)
    assert ll.lifetime.connectable
    assert ll.lifetime.visible
    assert ll.lifetime.MIN_LENGTH == ll.lifetime.min_length


def test_message_glue_cd(diagram):
    """Test gluing message on communication diagram."""

    lifeline1 = diagram.create(LifelineItem)
    lifeline2 = diagram.create(LifelineItem)
    message = diagram.create(MessageItem)

    # make second lifeline to be in sequence diagram mode
    lifeline2.lifetime.visible = True

    # connect head of message to lifeline's head
    connect(message, message.head, lifeline1)

    glued = allow(message, message.tail, lifeline2, lifeline2.lifetime.port)
    # no connection possible as 2nd lifeline is in sequence diagram
    # mode
    assert not glued


def test_message_glue_sd(diagram):
    """Test gluing message on sequence diagram."""

    msg = diagram.create(MessageItem)
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)

    # 1st lifeline - communication diagram
    # 2nd lifeline - sequence diagram
    ll2.lifetime.visible = True

    # connect lifetime of message to lifeline's lifetime
    connect(msg, msg.head, ll1, ll1.lifetime.port)

    glued = allow(msg, msg.tail, ll2)
    # no connection possible as 2nd lifeline is in communication
    # diagram mode
    assert not glued


def test_messages_disconnect_cd(diagram, element_factory):
    """Test disconnecting messages on communication diagram
    """
    ll1 = diagram.create(LifelineItem)
    ll2 = diagram.create(LifelineItem)
    msg = diagram.create(MessageItem)

    connect(msg, msg.head, ll1)
    connect(msg, msg.tail, ll2)

    subject = msg.subject

    assert subject.sendEvent
    assert subject.receiveEvent

    messages = element_factory.lselect(lambda e: e.isKindOf(UML.Message))
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    # verify integrity of messages
    assert 1 == len(messages)
    assert 2 == len(occurrences)


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


def test_message_disconnect_from_execution_specification(diagram, element_factory):
    """Test gluing message on sequence diagram."""

    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    exec_spec = diagram.create(ExecutionSpecificationItem)
    message = diagram.create(MessageItem)
    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)
    connect(message, message.head, exec_spec, exec_spec.ports()[0])

    disconnect(message, message.head)

    messages = element_factory.lselect(lambda e: e.isKindOf(UML.Message))
    occurrences = element_factory.lselect(
        lambda e: e.isKindOf(UML.MessageOccurrenceSpecification)
    )

    assert not message.subject
    assert not len(messages)
    assert not len(occurrences)
