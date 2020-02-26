"""Message item connection adapters."""

from typing import Optional

from gaphor import UML
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.interactions.executionspecification import (
    ExecutionSpecificationItem,
)
from gaphor.diagram.interactions.lifeline import LifelineItem
from gaphor.diagram.interactions.message import MessageItem
from gaphor.diagram.presentation import ElementPresentation


@Connector.register(LifelineItem, MessageItem)
class MessageLifelineConnect(BaseConnector):
    """Connect lifeline with a message.

    A message can connect to both the lifeline's head (the rectangle)
    or the lifetime line. In case it's added to the head, the message
    is considered to be part of a communication diagram. If the message is
    added to a lifetime line, it's considered a sequence diagram.
    """

    element: LifelineItem
    line: MessageItem

    def connect_lifelines(self, line, send, received):
        """
        Always create a new Message with two EventOccurrence instances.
        """

        def get_subject():
            if not line.subject:
                message = line.model.create(UML.Message)
                message.name = "call()"
                line.subject = message
            return line.subject

        if send:
            message = get_subject()
            if not message.sendEvent:
                event = message.model.create(UML.MessageOccurrenceSpecification)
                event.sendMessage = message
                event.covered = send.subject

        if received:
            message = get_subject()
            if not message.receiveEvent:
                event = message.model.create(UML.MessageOccurrenceSpecification)
                event.receiveMessage = message
                event.covered = received.subject

    def disconnect_lifelines(self, line):
        """
        Disconnect lifeline and set appropriate kind of message item. If
        there are no lifelines connected on both ends, then remove the message
        from the data model.
        """
        send: Optional[UML.Presentation[UML.Element]] = self.get_connected(line.head)
        received = self.get_connected(line.tail)

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
        if not send or not received:
            # Both ends are disconnected:
            message = line.subject
            del line.subject
            if not message.presentation:
                message.unlink()

    def allow(self, handle, port):
        """
        Glue to lifeline's head or lifetime. If lifeline's lifetime is
        visible then disallow connection to lifeline's head.
        """
        element = self.element
        lifetime = element.lifetime
        line = self.line
        opposite = line.opposite(handle)

        ol = self.get_connected(opposite)
        if ol:
            assert isinstance(ol, LifelineItem)
            opposite_is_visible = ol.lifetime.visible
            # connect lifetimes if both are visible or both invisible
            return not (lifetime.visible ^ opposite_is_visible)

        return not (lifetime.visible ^ (port is element.lifetime.port))

    def connect(self, handle, port):
        super().connect(handle, port)

        line = self.line
        send = self.get_connected(line.head)
        received = self.get_connected(line.tail)
        self.connect_lifelines(line, send, received)

        lifetime = self.element.lifetime
        # if connected to head, then make lifetime invisible
        if port is lifetime.port:
            lifetime.min_length = lifetime.MIN_LENGTH_VISIBLE
        else:
            lifetime.visible = False
            lifetime.connectable = False

    def disconnect(self, handle):
        assert self.canvas

        line = self.line
        received = self.get_connected(line.tail)
        lifeline = self.element
        lifetime = lifeline.lifetime

        # if a message is delete message, then disconnection causes
        # lifeline to be no longer destroyed (note that there can be
        # only one delete message connected to lifeline)
        if received and line.subject.messageSort == "deleteMessage":
            assert isinstance(received, LifelineItem)
            received.is_destroyed = False
            received.request_update()

        self.disconnect_lifelines(line)

        if len(list(self.canvas.get_connections(connected=lifeline))) == 1:
            # after disconnection count of connected items will be
            # zero, so allow connections to lifeline's lifetime
            lifetime.connectable = True
            lifetime.min_length = lifetime.MIN_LENGTH


@Connector.register(LifelineItem, ExecutionSpecificationItem)
class LifelineExecutionSpecificationConnect(BaseConnector):

    element: LifelineItem
    line: ExecutionSpecificationItem

    def allow(self, handle, port):
        lifetime = self.element.lifetime
        return lifetime.visible

    def connect(self, handle, port):
        lifeline = self.element.subject
        exec_spec: UML.ExecutionSpecification = self.line.subject
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

        canvas = self.line.canvas
        assert canvas
        for cinfo in canvas.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).connect(cinfo.handle, cinfo.port)
        return True

    def disconnect(self, handle):
        exec_spec: Optional[UML.ExecutionSpecification] = self.line.subject
        del self.line.subject
        if exec_spec:
            exec_spec.unlink()

        canvas = self.canvas
        assert canvas
        for cinfo in canvas.get_connections(connected=self.line):
            Connector(self.line, cinfo.item).disconnect(cinfo.handle)


@Connector.register(ExecutionSpecificationItem, ExecutionSpecificationItem)
class ExecutionSpecificationExecutionSpecificationConnect(BaseConnector):

    element: ExecutionSpecificationItem
    line: ExecutionSpecificationItem

    def allow(self, _handle, _port):
        return True

    def connect(self, handle, _port):
        parent_exec_spec = self.element.subject
        child_exec_spec: UML.ExecutionSpecification = self.line.subject
        model = self.element.model

        if not parent_exec_spec:
            # Can connect child exec spec if parent is not connected
            return True

        connected_item: Optional[UML.Presentation[UML.Element]] = self.get_connected(
            self.element.handles()[0]
        )
        assert connected_item
        return Connector(connected_item, self.line).connect(handle, None)

    def disconnect(self, handle):
        exec_spec: Optional[UML.ExecutionSpecification] = self.line.subject
        del self.line.subject
        if exec_spec:
            exec_spec.unlink()

        # TODO: also disconnect items connected to this item
