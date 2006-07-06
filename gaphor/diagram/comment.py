"""
CommentItem diagram item
"""

import gobject
import pango
import diacanvas

from gaphor import UML

from elementitem import ElementItem
from gaphas.item import NW

class CommentItem(ElementItem):
    # implements (Editable)

    __uml__ = UML.Comment

    EAR=15
    OFFSET=5
    FONT='sans 10'

    popup_menu = (
        'EditItem',
        'separator',
        'EditDelete',
    )

    def __init__(self, id=None):
        ElementItem.__init__(self, id)
        self.min_width = CommentItem.EAR + 2 * CommentItem.OFFSET
        self.height = 50
        self.width = 100
        #self._border = diacanvas.shape.Path()
        #self._border.set_line_width(2.0)
        #self._body = diacanvas.shape.Text()
        #self._body.set_font_description(pango.FontDescription(CommentItem.FONT))
        #self._body.set_markup(False)
        #self._body.set_pos((CommentItem.OFFSET, CommentItem.OFFSET))

    def postload(self):
        #self._body.set_text(self.subject.body or '')
        pass

    def edit(self):
        #self.start_editing(self._body)
        pass

    def on_subject_notify(self, pspec):
        """See DiagramItem.on_subject_notify()."""
        ElementItem.on_subject_notify(self, pspec, ('body',))

        ##if self.subject:
        #    self.on_subject_notify__body(self.subject, None)
        self.request_update()

    def on_subject_notify__body(self, subject, pspec):
        #print 'on_subject_notify__body: %s' % self.subject.body
        #self.sbody.set_text(self.subject.body or '')
        self.request_update()

    # DiaCanvasItem callbacks:

    def pre_update(self, context):
        # TODO: calc comment box bounds based on self.subject.body
        ElementItem.pre_update(self, context)

    def update(self, context):
        ElementItem.update(self, context)

    def draw(self, context):
        c = context.cairo
        # Width and height, adjusted for line width...
        ox = float(self._handles[NW].x)
        oy = float(self._handles[NW].y)
        w = self.width + ox
        h = self.height + oy
        ear = CommentItem.EAR
        c.move_to(w - ear, oy)
        line_to = c.line_to
        line_to(w - ear, oy + ear)
        line_to(w, oy + ear)
        line_to(w - ear, oy)
        line_to(ox, oy)
        line_to(ox, h)
        line_to(w, h)
        line_to(w, oy + ear)
        #c.show_text(self.subject.body or '')

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        return self._body

    def on_editable_start_editing(self, shape):
        self.preserve_property('body')

    def on_editable_editing_done(self, shape, new_text):
        if new_text != self.subject.body:
            self.subject.body = new_text
        #self._body.set_text(new_text)
        self.request_update()

# vim:sw=4
