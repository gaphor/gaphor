'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4:et

import gobject
import pango
import diacanvas

from gaphor import resource, UML
from gaphor.diagram import initialize_item

from gaphor.diagram.diagramline import DiagramLine

#
# TODO: asynch message has open arrow head
# synch message: closed arrow head, open arrow head and a dashed line.
# object creation: open arrow head, dashed line.

#Syntax for the Message name is the following:
#  messageident ::= [attribute =] signal-or-operation-name [ ( arguments) ][: return-value] | *
#  arguments ::= argument [ , arguments]
#  argument ::= [parameter-name=]argument-value | attribute= out-parameter-name [:argument-value]| -
#
# Message.signature points to the operation or signal that is executed
# Message.arguments provides a list of arguments for the operation.
#
class MessageItem(DiagramLine, diacanvas.CanvasEditable):
    
    FONT='sans 10'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        self.set(has_tail=1, tail_fill_color=0, tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)

        self._label = diacanvas.shape.Text()
        self._label.set_font_description(pango.FontDescription(MessageItem.FONT))
        self._label.set_markup(False)
        #self._label.set_text('blah')

    def save (self, save_func):
        DiagramLine.save(self, save_func)

    def load (self, name, value):
        DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramLine.on_subject_notify(self, pspec,
                                      notifiers + ('name',))

        self.on_subject_notify__name(self.subject, pspec)

    def on_subject_notify__name(self, subject, pspec):
        #log.debug('Association name = %s' % (subject and subject.name))
        if subject:
            self._label.set_text(subject.name or '')
        else:
            self._label.set_text('')
        self.request_update()

    def update_label(self, p1, p2):
        """Update the name label near the middle of the association.
        """
        w, h = self._label.to_pango_layout(True).get_pixel_size()

        x = p1[0] > p2[0] and w + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] <= p2[1] and h or 0
        y = (p1[1] + p2[1]) / 2.0 - y

        self._label.set_pos((x, y))
        #log.debug('label pos = (%d, %d)' % (x, y))
        #return x, y, max(x + 10, x + w), max(y + 10, y + h)
        return x, y, x + w, y + h

    def on_update(self, affine):
        DiagramLine.on_update(self, affine)

        handles = self.handles
        middle = len(handles)/2
        b1 = self.update_label(handles[middle-1].get_pos_i(),
                               handles[middle].get_pos_i())

        bv = zip(b1, self.bounds)
        self.set_bounds((min(bv[0]), min(bv[1]), max(bv[2]), max(bv[3])))

    def on_shape_iter(self):
        for s in DiagramLine.on_shape_iter(self):
            yield s
        yield self._label

    # Gaphor Connection Protocol

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.Lifeline)
        except AttributeError:
            return 0

    def confirm_connect_handle(self, handle):
        """See RelationshipItem.confirm_connect_handle().

        Always create a new Message with two EventOccurence instances.
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            if self.subject and \
               self.subject.sendEvent.covered is s1 and \
               self.subject.receiveEvent.covered is s2:
                return

            factory = resource(UML.ElementFactory)
            message = factory.create(UML.Message)
            message.messageKind = 'complete'
            head_event = factory.create(UML.EventOccurrence)
            head_event.sendMessage = message
            head_event.covered = s1

            tail_event = factory.create(UML.EventOccurrence)
            tail_event.receiveMessage = message
            tail_event.covered = s2

            self.set_subject(message)

    def confirm_disconnect_handle(self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        self.set_subject(None)

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        log.debug('association edit on (%d,%d)' % (x, y))
        #p = (x, y)
        #drp = diacanvas.geometry.distance_rectangle_point
        #if drp(self._label_bounds, p) < 1.0:
        return self._label

    def on_editable_start_editing(self, shape):
        pass

    def on_editable_editing_done(self, shape, new_text):
        if self.subject and self.subject.name != new_text:
            self.subject.name = new_text

initialize_item(MessageItem)
