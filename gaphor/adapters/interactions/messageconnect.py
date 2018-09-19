#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License
# more details.
#
# You should have received a copy of the GNU Library General Public
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Message item connection adapters.
"""

from __future__ import absolute_import
from gaphor.adapters.connectors import AbstractConnect
from zope import interface, component
from gaphor.UML import uml2
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
                message = self.element_factory.create(uml2.Message)
                message.name = 'call()'
                line.subject = message
            return line.subject

        if send:
            message = get_subject()
            if not message.sendEvent:
                event = self.element_factory.create(uml2.MessageOccurrenceSpecification)
                event.sendMessage = message
                event.covered = send.subject

        if received:
            message = get_subject()
            if not message.receiveEvent:
                event = self.element_factory.create(uml2.MessageOccurrenceSpecification)
                event.receiveMessage = message
                event.covered = received.subject


    def disconnect_lifelines(self, line):
        """
        Disconnect lifeline and set appropriate kind of message item. If
        there are no lifelines connected on both ends, then remove the message
        from the data model.
        """
        send = self.get_connected(line.head)
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
            for message in list(line._messages):
                line.remove_message(message, False)
                message.unlink()

            for message in list(line._inverted_messages):
                line.remove_message(message, True)
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
            opposite_is_visible = ol.lifetime.visible
            # connect lifetimes if both are visible or both invisible
            return not (lifetime.visible ^ opposite_is_visible)

        return not (lifetime.visible ^ (port is element.lifetime.port))
        

    def connect(self, handle, port):
        super(MessageLifelineConnect, self).connect(handle, port)

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
        super(MessageLifelineConnect, self).disconnect(handle)

        line = self.line
        send = self.get_connected(line.head)
        received = self.get_connected(line.tail)
        lifeline = self.element
        lifetime = lifeline.lifetime

        # if a message is delete message, then disconnection causes
        # lifeline to be no longer destroyed (note that there can be
        # only one delete message connected to lifeline)
        if received and line.subject.messageSort == 'deleteMessage':
            received.is_destroyed = False
            received.request_update()

        self.disconnect_lifelines(line)

        if len(list(self.canvas.get_connections(connected=lifeline))) == 1:
            # after disconnection count of connected items will be
            # zero, so allow connections to lifeline's lifetime
            lifetime.connectable = True
            lifetime.min_length = lifetime.MIN_LENGTH
            


component.provideAdapter(MessageLifelineConnect)

