"""
Message item connection adapters.
"""

from gaphor.adapters.connectors import AbstractConnect
from zope import interface, component
from gaphor import UML
from gaphor.diagram import items

class MessageLifelineConnect(AbstractConnect):
    """
    Connect lifeline with a message.

    A message can connect to both the lifeline's head (the rectangle)
    or the lifetime line. In case it's added to the head, the message
    is considered to be part of a communication diagram. If the message is
    added to a lifetime line, it's considered a sequence diagram.
    """

    component.adapts(items.LifelineItem, items.MessageItem)

    def connect_lifelines(self, line, send, received):
        """
        Always create a new Message with two EventOccurence instances.
        """
        def get_subject():
            if not line.subject:
                message = self.element_factory.create(UML.Message)
                message.name = 'call()'
                line.subject = message
            return line.subject

        if send:
            message = get_subject()
            if not message.sendEvent:
                event = self.element_factory.create(UML.EventOccurrence)
                event.sendMessage = message
                event.covered = send.subject

        if received:
            message = get_subject()
            if not message.receiveEvent:
                event = self.element_factory.create(UML.EventOccurrence)
                event.receiveMessage = message
                event.covered = received.subject


    def disconnect_lifelines(self, line):
        """
        Disconnect lifeline and set appropriate kind of message item. If
        there are no lifelines connected on both ends, then remove the message
        from the data model.
        """
        send = line.head.connected_to
        received = line.tail.connected_to

        if send:
            event = line.subject.receiveEvent
            if event:
                event.unlink()

        if received:
            event = line.subject.sendEvent
            if event:
                event.unlink()

        if not send and not received:
            # Both ends are disconnected:
            message = line.subject
            del line.subject
            if not message.presentation:
                message.unlink()
            for message in list(line._messages):
                line.remove_message(message, False)
                message.unlink()

            for message in list(line._inverted_messages):
                line.remove_message(message, True)
                message.unlink()


    def _glue_lifetime(self, handle):
        """
        Glue ``handle`` to lifeline's lifetime.

        The position returned is in line coordinates.
        """
        lifetime = self.element.lifetime
        top = lifetime.top.pos
        bottom = lifetime.bottom.pos

        pos = self._matrix_l2e.transform_point(*handle.pos)
        d, pos = geometry.distance_line_point(top, bottom, pos)

        return self._matrix_e2l.transform_point(*pos)


    def glue(self, handle, port):
        """
        Glue to lifeline's head or lifetime. If lifeline's lifetime is
        visible then disallow connection to lifeline's head.
        """
        element = self.element
        lifetime = element.lifetime
        line = self.line
        opposite = line.opposite(handle)

        pos = None
        if opposite.connected_to:
            opposite_is_visible = opposite.connected_to.lifetime.is_visible

            if lifetime.is_visible and opposite_is_visible:
                # glue lifetimes if both are visible
                pos = self._glue_lifetime(handle)
            elif not lifetime.is_visible and not opposite_is_visible:
                # glue heads if both lifetimes are invisible
                pos = AbstractConnect.glue(self, handle)

        elif lifetime.is_visible:
            pos = self._glue_lifetime(handle)

        else:
            pos = AbstractConnect.glue(self, handle)
        return pos
        

    def _get_segment(self, handle):
        """
        Return handles of one of lifeline head's side or lifetime handles.
        """
        element = self.element
        if element.lifetime.is_visible:
            return element.handles()[-2:] # return lifeline's lifetime handles
        else:
            return super(MessageLifelineConnect, self)._get_segment(handle)
        assert False


    def connect(self, handle, port):
        if not AbstractConnect.connect(self, handle, port):
            return

        line = self.line
        send = line.head.connected_to
        received = line.tail.connected_to
        self.connect_lifelines(line, send, received)

        lifetime = self.element.lifetime
        # if no lifetime then disallow making lifetime visible
        if not lifetime.is_visible:
            lifetime.bottom.movable = False
        # todo: move code above to LifetimeItem class
        lifetime._messages_count += 1


    def disconnect(self, handle):
        line = self.line
        send = line.head.connected_to
        received = line.tail.connected_to

        # if a message is delete message, then disconnection causes
        # lifeline to be no longer destroyed (note that there can be
        # only one delete message connected to lifeline)
        if received and line.subject.messageSort == 'deleteMessage':
            received.lifetime.is_destroyed = False
            received.request_update()

        AbstractConnect.disconnect(self, handle)
        self.disconnect_lifelines(line)

        lifetime = self.element.lifetime
        lifetime._messages_count -= 1
        # if there are no messages connected then allow to make lifetime visible
        # todo: move code below to LifetimeItem class
        if lifetime._messages_count < 1:
            lifetime.bottom.movable = True


component.provideAdapter(MessageLifelineConnect)

