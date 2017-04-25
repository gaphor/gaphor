"""
Sequence and communication diagram messages.

Messages are implemented according to UML 2.1.1 specification.

Implementation Details
======================
Message sort is supported but occurence specification is not implemented.
This means that model drawn on a diagram is not complete on UML datamodel
level, still it is valid UML diagram (see Lifelines Diagram in UML
specification, page 461).

Reply Messages
--------------
Different sources show that reply message has filled arrow, including
UML 2.0.

UML 2.1.1 specification says that reply message should be drawn with an
open arrow. This is visible on examples in UML 2.0 and UML 2.1.1
specifications.

Asynchronous Signal
--------------------
It is not clear how to draw signals. It is usually drawn with a half-open
arrow.  This approach is used in Gaphor, too.

Delete Message
--------------
Different sources show that delete message has a "X" at the tail.
It does not seem to be correct solution. A "X" should be shown
at the end of lifeline's lifetime instead (see ``lifeline`` module
documentation for more information).

Events
------
Occurence specification is not implemented, therefore
- no events implemented (i.e. destroy event)
- no message sequence number on communication diagram

Operations
----------
``Lifeline.represents`` attribute is ``None``, so it is not possible to
specify operation (or signal) for a message. Instead, one has to put
operation information in message's name.

See also ``lifeline`` module documentation.
"""

from __future__ import absolute_import
from math import pi

from gaphas.util import path_ellipse

from gaphor.diagram.diagramline import NamedLine
from gaphor.misc.odict import odict
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM

PI_2 = pi / 2

class MessageItem(NamedLine):
    """
    Message item is drawn on sequence and communication diagrams.

    On communication diagram, message item is decorated with an arrow in
    the middle of a line.

    Attributes:

    - _is_communication: check if message is on communication diagram
    - _arrow_pos: decorating arrow position
    - _arrow_angle: decorating arrow angle
    """

    __style__ = {
        'name-align-str': ':',
    }

    # name padding on sequence diagram
    SD_PADDING = NamedLine.style.name_padding

    # name padding on communication diagram
    CD_PADDING = (10, 10, 10, 10)

    def __init__(self, id=None):
        super(MessageItem, self).__init__(id)
        self._is_communication = False
        self._arrow_pos = 0, 0
        self._arrow_angle = 0
        self._messages = odict()
        self._inverted_messages = odict()


    def pre_update(self, context):
        """
        Update communication diagram information.
        """
        self._is_communication = self.is_communication()
        if self._is_communication:
            self._name.style.text_padding = self.CD_PADDING
        else:
            self._name.style.text_padding = self.SD_PADDING

        super(MessageItem, self).pre_update(context)


    def post_update(self, context):
        """
        Update communication diagram information.
        """
        super(MessageItem, self).post_update(context)

        if self._is_communication:
            pos, angle = self._get_center_pos()
            self._arrow_pos = pos
            self._arrow_angle = angle


    def save(self, save_func):
        save_func('message', list(self._messages), reference=True)
        save_func('inverted', list(self._inverted_messages), reference=True)

        super(MessageItem, self).save(save_func)


    def load(self, name, value):
        if name == 'message':
            #print 'message! value =', value
            self.add_message(value, False)
        elif name == 'inverted':
            #print 'inverted! value =', value
            self.add_message(value, True)
        else:
            super(MessageItem, self).load(name, value)


    def postload(self):
        for message in self._messages:
            self.set_message_text(message, message.name, False)

        for message in self._inverted_messages:
            self.set_message_text(message, message.name, True)

        super(MessageItem, self).postload()


    def _draw_circle(self, cr):
        """
        Draw circle for lost/found messages.
        """
        # method is called by draw_head or by draw_tail methods,
        # so draw in (0, 0))
        cr.set_line_width(0.01)
        cr.arc(0.0, 0.0, 4, 0.0, 2 * pi)
        cr.fill()


    def _draw_arrow(self, cr, half=False, filled=True):
        """
        Draw an arrow.

        Parameters:

        - half: draw half-open arrow
        - filled: draw filled arrow
        """
        cr.move_to(15, 6)
        cr.line_to(0, 0)
        if not half:
            cr.line_to(15, -6)
        if filled:
            cr.close_path()
            cr.fill_preserve()


    def draw_head(self, context):
        cr = context.cairo
        # no head drawing in case of communication diagram
        if self._is_communication:
            cr.move_to(0, 0)
            return

        cr.move_to(0, 0)

        subject = self.subject
        if subject and subject.messageKind == 'found':
            self._draw_circle(cr)
            cr.stroke()

        cr.move_to(0, 0)


    def draw_tail(self, context):
        cr = context.cairo

        # no tail drawing in case of communication diagram
        if self._is_communication:
            cr.line_to(0, 0)
            return

        subject = self.subject

        if subject and subject.messageSort in ('createMessage', 'reply'):
            cr.set_dash((7.0, 5.0), 0)

        cr.line_to(0, 0)
        cr.stroke()

        cr.set_dash((), 0)

        if subject:
            w = cr.get_line_width()
            if subject.messageKind == 'lost':
                self._draw_circle(cr)
                cr.stroke()

            cr.set_line_width(w)
            half = subject.messageSort == 'asynchSignal'
            filled = subject.messageSort in ('synchCall', 'deleteMessage')
            self._draw_arrow(cr, half, filled)
        else:
            self._draw_arrow(cr)

        cr.stroke()


    def _draw_decorating_arrow(self, cr, inverted=False):
        cr.save()
        try:
            angle = self._arrow_angle

            hint = -1

            # rotation hint, keep arrow on the same side as message text
            # elements
            if abs(angle) >= PI_2 and angle != -PI_2:
                hint = 1

            if inverted:
                angle += hint * pi

            x, y = self._arrow_pos

            # move to arrow pos and rotate, below we operate in horizontal
            # mode
            cr.translate(x, y)
            cr.rotate(angle)
            # add some padding
            cr.translate(0, 6 * hint)

            # draw decorating arrow
            d = 15
            dr = d - 4
            r = 3
            cr.set_line_width(1.5)
            cr.move_to(-d, 0)
            cr.line_to(d, 0)
            cr.line_to(dr, r)
            cr.move_to(dr, -r)
            cr.line_to(d, 0)
            cr.stroke()
        finally:
            cr.restore()


    def draw(self, context):
        super(MessageItem, self).draw(context)

        # on communication diagram draw decorating arrows for messages and
        # inverted messages
        if self._is_communication:
            cr = context.cairo
            self._draw_decorating_arrow(cr)
            if len(self._inverted_messages) > 0:
                self._draw_decorating_arrow(cr, True)


    def is_communication(self):
        """
        Check if message is connecting to lifelines on communication
        diagram.
        """
        canvas = self.canvas
        c1 = canvas.get_connection(self.head)
        c2 = canvas.get_connection(self.tail)
        return c1 and not c1.connected.lifetime.visible \
                or c2 and not c2.connected.lifetime.visible


    def add_message(self, message, inverted):
        """
        Add message onto communication diagram.
        """
        if inverted:
            messages = self._inverted_messages
            style = {
                'text-align-group': 'inverted',
                'text-align': (ALIGN_CENTER, ALIGN_BOTTOM),
            }
        else:
            messages = self._messages
            group = 'stereotype'
            style = {
                'text-align-group': 'stereotype',
            }

        style['text-align-str'] = ':'
        style['text-padding'] = self.CD_PADDING
        txt = self.add_text('name', style=style)
        txt.text = message.name
        messages[message] = txt
        self.request_update()


    def remove_message(self, message, inverted):
        """
        Remove message from communication diagram.
        """
        if inverted:
            messages = self._inverted_messages
        else:
            messages = self._messages
        txt = messages[message]
        self.remove_text(txt)
        del messages[message]
        self.request_update()


    def set_message_text(self, message, text, inverted):
        """
        Set text of message on communication diagram.
        """
        if inverted:
            messages = self._inverted_messages
        else:
            messages = self._messages
        messages[message].text = text
        self.request_update()


    def swap_messages(self, m1, m2, inverted):
        """
        Swap order of two messages on communication diagram.
        """
        if inverted:
            messages = self._inverted_messages
        else:
            messages = self._messages
        t1 = messages[m1]
        t2 = messages[m2]
        self.swap_texts(t1, t2)
        messages.swap(m1, m2)
        self.request_update()
        return True


# vim:sw=4:et
