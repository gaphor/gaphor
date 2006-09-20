"""
CommentItem diagram item
"""

import gobject
import pango
from zope import component

from gaphor import UML
from elementitem import ElementItem
from gaphas.item import NW
from gaphas.util import text_multiline, text_extents

from interfaces import IEditor

class CommentItem(ElementItem):

    __uml__ = UML.Comment

    EAR=15
    OFFSET=5

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
        print 'on_subject_notify__body: %s' % self.subject.body
        #self.sbody.set_text(self.subject.body or '')
        self.request_update()

    # DiaCanvasItem callbacks:

    def pre_update(self, context):
        if not self.subject: return
        cr = context.cairo
        w, h = text_extents(cr, self.subject.body, multiline=True, padding=2)
        self.min_width = w + 10
        self.min_height = h + 20
        ElementItem.pre_update(self, context)

    def update(self, context):
        ElementItem.update(self, context)

    def draw(self, context):
        if not self.subject: return
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
        c.stroke()
	if self.subject.body:
	    # Do not print empty string, since cairo-win32 can't handle it.
            text_multiline(c, 5, 5, self.subject.body, padding=2)
	    #c.move_to(10, 15)
	    #c.show_text(self.subject.body)

# vim:sw=4
