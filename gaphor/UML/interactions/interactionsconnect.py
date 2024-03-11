"""Message item connection adapters."""

from typing import Optional

from gaphor import UML
from gaphor.core.modeling import Element, Presentation
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.group import group
from gaphor.UML.interactions.executionspecification import ExecutionSpecificationItem
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.interactions.message import MessageItem


def get_connected(item, handle) -> Optional[Presentation[Element]]:
    """Get item connected to a handle."""
    if cinfo := item.diagram.connections.get_connection(handle):
        return cinfo.connected  # type: ignore[no-any-return] # noqa: F723
    return None


def get_lifeline(item, handle):
    connected_item = get_connected(item, handle)
    if connected_item is None or isinstance(connected_item, LifelineItem):
        return connected_item
    return get_lifeline(connected_item, connected_item.handles()[0])


def order_lifeline_covered_by(lifeline):
    diagram = lifeline.diagram

    def y_and_occurrence(connected):
        for conn in diagram.connections.get_connections(connected=connected):
            m = conn.item.matrix_i2c
            if not conn.item.subject:
                # Can happen during DnD
                continue
            if isinstance(conn.item, ExecutionSpecificationItem):
                yield (
                    m.transform_point(*conn.item.top.pos)[1],
                    conn.item.subject.start,
                )
                yield (
                    m.transform_point(*conn.item.bottom.pos)[1],
                    conn.item.subject.finish,
                )
                yield from y_and_occurrence(conn.item)
            elif isinstance(conn.item, MessageItem):
                yield (
                    m.transform_point(*conn.handle.pos)[1],
                    conn.item.subject.sendEvent
                    if conn.handle is conn.item.head
                    else conn.item.subject.receiveEvent,
                )

    if lifeline.subject:
        keys = {o: y for y, o in y_and_occurrence(lifeline)}
        lifeline.subject.coveredBy.order(lambda key: keys.get(key, 0.0))


def owner_for_message(line, lifeline):
    maybe_interaction = lifeline.parent
    if line.subject.interaction:
        return
    elif isinstance(maybe_interaction, InteractionItem):
        line.parent = maybe_interaction
        group(maybe_interaction, line)
    elif lifeline.subject and lifeline.subject.interaction:
        line.subject.interaction = lifeline.subject.interaction


def connect_lifelines(line, send, received):
    """Always create a new Message with two EventOccurrence instances."""

    def get_subject():
        if not line.subject:
            message = line.model.create(UML.Message)
            message.name = line.diagram.gettext("call()")
            line.subject = message
        return line.subject

    if send:
        message = get_subject()
        if not message.sendEvent:
            event = message.model.create(UML.MessageOccurrenceSpecification)
            event.sendMessage = message
            event.covered = send.subject
            order_lifeline_covered_by(send)
        owner_for_message(line, send)

    if received:
        message = get_subject()
        if not message.receiveEvent:
            event = message.model.create(UML.MessageOccurrenceSpecification)
            event.receiveMessage = message
            event.covered = received.subject
            order_lifeline_covered_by(received)
        owner_for_message(line, received)


def disconnect_lifelines(line, send, received):
    """Disconnect lifeline and set appropriate kind of message item.

    If there are no lifelines connected on both ends, then remove the
    message from the data model.
    """
    if not (subject := line.subject):
        return

    if send and (event := subject.sendEvent):
        event.unlink()

    if received and (event := subject.receiveEvent):
        event.unlink()

    # one is disconnected and one is about to be disconnected,
    # so destroy the message
    if not (subject.sendEvent or subject.receiveEvent):
        # Both ends are disconnected: remove subject
        del line.subject


@Connector.register(LifelineItem, MessageItem)
class MessageLifelineConnect(BaseConnector):
    """Connect lifeline with a message.

    A message can connect to both the lifeline's head (the rectangle) or
    the lifetime line. In case it's added to the head, the message is
    considered to be part of a communication diagram. If the message is
    added to a lifetime line, it's considered a sequence diagram.

    Message.head has no arrow (sendEvent)
    Message.tail has the arrow (receiveEvent)
    """

    element: LifelineItem
    line: MessageItem

    def connect(self, handle, port):
        line = self.line
        send = get_lifeline(line, line.head)
        received = get_lifeline(line, line.tail)
        connect_lifelines(line, send, received)
        return True

    def disconnect(self, handle):
        line = self.line
        send: Optional[Presentation[Element]] = get_connected(line, line.head)
        received = self.get_connected(line.tail)

        # if a message is a deleted message, then the disconnection causes
        # the lifeline to be no longer destroyed (note that there can be
        # only one delete message connected to lifeline)
        if received and line.subject and line.subject.messageSort == "deleteMessage":
            assert isinstance(received, LifelineItem)
            received.is_destroyed = False
            received.request_update()

        disconnect_lifelines(
            line,
            send and handle is line.head,
            received and handle is line.tail,
        )


@Connector.register(ExecutionSpecificationItem, MessageItem)
class ExecutionSpecificationMessageConnect(BaseConnector):
    element: ExecutionSpecificationItem
    line: MessageItem

    def connect(self, handle, _port):
        line = self.line
        send = get_lifeline(line, line.head)
        received = get_lifeline(line, line.tail)
        connect_lifelines(line, send, received)
        return True

    def disconnect(self, handle):
        line = self.line
        send = get_lifeline(line, line.head)
        received = get_lifeline(line, line.tail)
        disconnect_lifelines(
            line,
            send and handle is line.head,
            received and handle is line.tail,
        )


@Connector.register(LifelineItem, ExecutionSpecificationItem)
class LifelineExecutionSpecificationConnect(BaseConnector):
    element: LifelineItem
    line: ExecutionSpecificationItem

    def allow(self, handle, port):
        lifetime = self.element.lifetime
        return super().allow(handle, port) and lifetime.visible

    def connect(self, handle, port):
        lifeline = self.element.subject
        exec_spec = self.line.subject
        model = self.element.model
        if not exec_spec:
            exec_spec = model.create(UML.BehaviorExecutionSpecification)
            self.line.subject = exec_spec

            start_occurrence: UML.ExecutionOccurrenceSpecification = model.create(
                UML.ExecutionOccurrenceSpecification
            )
            start_occurrence.covered = lifeline
            start_occurrence.execution = exec_spec

            finish_occurrence: UML.ExecutionOccurrenceSpecification = model.create(
                UML.ExecutionOccurrenceSpecification
            )
            finish_occurrence.covered = lifeline
            finish_occurrence.execution = exec_spec

        if lifeline.interaction:
            exec_spec.enclosingInteraction = lifeline.interaction

        if self.line.parent is not self.element:
            self.line.change_parent(self.element)

        for cinfo in self.diagram.connections.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).connect(cinfo.handle, cinfo.port)
        return True

    def disconnect(self, handle):
        del self.line.subject

        if self.line.parent is self.element:
            new_parent = self.element.parent
            self.line.change_parent(new_parent)

        for cinfo in self.diagram.connections.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).disconnect(cinfo.handle)


@Connector.register(ExecutionSpecificationItem, ExecutionSpecificationItem)
class ExecutionSpecificationExecutionSpecificationConnect(BaseConnector):
    element: ExecutionSpecificationItem
    line: ExecutionSpecificationItem

    def connect(self, handle, _port):
        parent_exec_spec = self.element.subject

        if not parent_exec_spec:
            # Can connect child exec spec if parent is not connected
            return True

        connected_item: Optional[Presentation[Element]]
        connected_item = self.get_connected(self.element.handles()[0])
        assert connected_item
        Connector(connected_item, self.line).connect(handle, None)

        self.line.change_parent(self.element)

        return True

    def disconnect(self, handle):
        del self.line.subject

        for cinfo in self.diagram.connections.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).disconnect(cinfo.handle)
