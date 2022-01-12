"""Message item connection adapters."""

from typing import Optional

from gaphas.connector import ConnectionSink, ItemConnectionSink
from gaphas.types import Pos, SupportsFloatPos

from gaphor import UML
from gaphor.core.modeling import Element, Presentation
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.grouping import Group
from gaphor.i18n import gettext
from gaphor.UML.interactions.executionspecification import ExecutionSpecificationItem
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.interactions.message import MessageItem


def get_connected(item, handle) -> Optional[Presentation[Element]]:
    """Get item connected to a handle."""
    cinfo = item.diagram.connections.get_connection(handle)
    if cinfo:
        return cinfo.connected  # type: ignore[no-any-return] # noqa: F723
    return None


def get_lifeline(item, handle):
    connected_item = get_connected(item, handle)
    if connected_item is None or isinstance(connected_item, LifelineItem):
        return connected_item
    return get_lifeline(connected_item, connected_item.handles()[0])


def order_lifeline_covered_by(lifeline):
    diagram = lifeline.diagram

    def y_and_occurence(connected):
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
                yield from y_and_occurence(conn.item)
            elif isinstance(conn.item, MessageItem):
                yield (
                    m.transform_point(*conn.handle.pos)[1],
                    conn.item.subject.sendEvent
                    if conn.handle is conn.item.head
                    else conn.item.subject.receiveEvent,
                )

    if lifeline.subject:
        keys = {o: y for y, o in y_and_occurence(lifeline)}
        lifeline.subject.coveredBy.order(lambda key: keys.get(key, 0.0))


def owner_for_message(line, lifeline):
    maybe_interaction = lifeline.parent
    if line.subject.interaction:
        return
    elif isinstance(maybe_interaction, InteractionItem):
        Group(maybe_interaction, line).group()
    elif lifeline.subject and lifeline.subject.interaction:
        line.subject.interaction = lifeline.subject.interaction


def connect_lifelines(line, send, received):
    """Always create a new Message with two EventOccurrence instances."""

    def get_subject():
        if not line.subject:
            message = line.model.create(UML.Message)
            message.name = gettext("call()")
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
    if not line.subject:
        return

    if send:
        event = line.subject.receiveEvent
        if event:
            event.unlink()

    if received:
        event = line.subject.sendEvent
        if event:
            event.unlink()

    # one is disconnected and one is about to be disconnected,
    # so destroy the message
    if not (send and received):
        # Both ends are disconnected:
        message = line.subject
        del line.subject
        if not message.presentation:
            message.unlink()


@Connector.register(LifelineItem, MessageItem)
class MessageLifelineConnect(BaseConnector):
    """Connect lifeline with a message.

    A message can connect to both the lifeline's head (the rectangle) or
    the lifetime line. In case it's added to the head, the message is
    considered to be part of a communication diagram. If the message is
    added to a lifetime line, it's considered a sequence diagram.
    """

    element: LifelineItem
    line: MessageItem

    def allow(self, handle, port):
        """Glue to lifeline's head or lifetime.

        If lifeline's lifetime is visible then disallow connection to
        lifeline's head.
        """
        element = self.element
        lifetime = element.lifetime
        line = self.line
        opposite = line.opposite(handle)

        ol = self.get_connected(opposite)
        if isinstance(ol, LifelineItem):
            opposite_is_visible = ol.lifetime.visible
            # connect lifetimes if both are visible or both invisible
            return not (lifetime.visible ^ opposite_is_visible)

        return not (lifetime.visible ^ (port is element.lifetime.port))

    def connect(self, handle, port):
        line = self.line
        send = self.get_connected(line.head)
        received = self.get_connected(line.tail)
        connect_lifelines(line, send, received)

        lifetime = self.element.lifetime
        # if connected to head, then make lifetime invisible
        if port is lifetime.port:
            lifetime.min_length = lifetime.MIN_LENGTH_VISIBLE
        else:
            lifetime.visible = False
            lifetime.connectable = False
        return True

    def disconnect(self, handle):
        line = self.line
        send: Optional[Presentation[Element]] = get_connected(line, line.head)
        received = self.get_connected(line.tail)
        lifeline = self.element
        lifetime = lifeline.lifetime

        # if a message is delete message, then disconnection causes
        # lifeline to be no longer destroyed (note that there can be
        # only one delete message connected to lifeline)
        if received and line.subject and line.subject.messageSort == "deleteMessage":
            assert isinstance(received, LifelineItem)
            received.is_destroyed = False
            received.request_update()

        disconnect_lifelines(line, send, received)

        if len(list(self.diagram.connections.get_connections(connected=lifeline))) == 1:
            # after disconnection count of connected items will be
            # zero, so allow connections to lifeline's lifetime
            lifetime.connectable = True
            lifetime.min_length = lifetime.MIN_LENGTH


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
        disconnect_lifelines(line, send, received)


@Connector.register(LifelineItem, ExecutionSpecificationItem)
class LifelineExecutionSpecificationConnect(BaseConnector):

    element: LifelineItem
    line: ExecutionSpecificationItem

    def allow(self, handle, port):
        lifetime = self.element.lifetime
        return lifetime.visible

    def connect(self, handle, port):
        lifeline = self.element.subject
        exec_spec = self.line.subject
        model = self.element.model
        if not exec_spec:
            exec_spec = model.create(UML.BehaviorExecutionSpecification)
            self.line.subject = exec_spec

            start_occurence: UML.ExecutionOccurrenceSpecification = model.create(
                UML.ExecutionOccurrenceSpecification
            )
            start_occurence.covered = lifeline
            start_occurence.execution = exec_spec

            finish_occurence: UML.ExecutionOccurrenceSpecification = model.create(
                UML.ExecutionOccurrenceSpecification
            )
            finish_occurence.covered = lifeline
            finish_occurence.execution = exec_spec

        if lifeline.interaction:
            exec_spec.enclosingInteraction = lifeline.interaction

        diagram = self.diagram
        if self.line.parent is not self.element:
            self.line.change_parent(self.element)

        for cinfo in diagram.connections.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).connect(cinfo.handle, cinfo.port)
        return True

    def disconnect(self, handle):
        exec_spec: Optional[UML.ExecutionSpecification] = self.line.subject
        del self.line.subject
        if exec_spec:
            exec_spec.unlink()

        diagram = self.diagram

        if self.line.parent is self.element:
            new_parent = self.element.parent
            self.line.change_parent(new_parent)

        for cinfo in diagram.connections.get_connections(connected=self.line):
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
        exec_spec: Optional[UML.ExecutionSpecification] = self.line.subject
        del self.line.subject
        if exec_spec and not exec_spec.presentation:
            exec_spec.unlink()

        for cinfo in self.diagram.connections.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).disconnect(cinfo.handle)


@ConnectionSink.register(LifelineItem)
class LifelineConnectionSink(ItemConnectionSink):
    def glue(
        self, pos: SupportsFloatPos, secondary_pos: Optional[SupportsFloatPos] = None
    ) -> Optional[Pos]:
        """Glue a line to the lifeline item, have a preference for the lifetime
        line."""
        assert isinstance(self.item, LifelineItem)
        glue_pos = super().glue(pos, secondary_pos)

        lifetime = self.item.lifetime
        if lifetime.visible and self.port is not lifetime.port:  # type: ignore[has-type]
            g, d = lifetime.port.glue(pos)
            if d < self.distance:
                self.port = lifetime.port
                glue_pos = g

            return glue_pos

        return glue_pos
