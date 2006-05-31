'''
CommentItem diagram item
'''
# vim:sw=4

import gobject
import pango
import diacanvas

from gaphor import UML

from elementitem import ElementItem

class CommentItem(ElementItem, diacanvas.CanvasEditable):

    __uml__ = UML.Comment

    __gproperties__ = {
        'body': (gobject.TYPE_STRING, 'body', '', '', gobject.PARAM_READWRITE)
    }

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
        self.set(min_width=CommentItem.EAR + 2 * CommentItem.OFFSET,
                 height=50, width=100)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)
        self._body = diacanvas.shape.Text()
        self._body.set_font_description(pango.FontDescription(CommentItem.FONT))
        #self._body.set_text_width(self.width - (CommentItem.OFFSET * 2))
        self._body.set_markup(False)
        self._body.set_pos((CommentItem.OFFSET, CommentItem.OFFSET))

    def postload(self):
        self._body.set_text(self.subject.body or '')

    def edit(self):
        self.start_editing(self._body)

    def do_set_property(self, pspec, value):
        if pspec.name == 'body':
            self.preserve_property('body')
            self.subject.body = value
        else:
            ElementItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'body':
            return self.subject.body
        else:
            return ElementItem.do_get_property(self, pspec)

    def on_subject_notify(self, pspec):
        """See DiagramItem.on_subject_notify()."""
        ElementItem.on_subject_notify(self, pspec, ('body',))

        if self.subject:
            self.on_subject_notify__body(self.subject, None)

    def on_subject_notify__body(self, subject, pspec):
        #print 'on_subject_notify__body: %s' % self.subject.body
        self._body.set_text(self.subject.body or '')
        self.request_update()

    # DiaCanvasItem callbacks:

    def on_update(self, affine):
        # Outline the text, first tell the text how width it may become:
        self._body.set_text_width(self.width - CommentItem.EAR - CommentItem.OFFSET)
        w, h = self._body.to_pango_layout(True).get_pixel_size()
        self.set(min_height=h + CommentItem.OFFSET * 2)
        #self._body.set_property('height', self.height - CommentItem.OFFSET * 2)
        #self.update_child(self._body, affine)
        ElementItem.on_update(self, affine)

        # Width and height, adjusted for line width...
        w = self.width
        h = self.height
        ear = CommentItem.EAR
        self._border.line(((w - ear, 0), (w- ear, ear), (w, ear), (w - ear, 0),
                            (0, 0), (0, h), (w, h), (w, ear)))
        self.expand_bounds(1)

    def on_event (self, event):
        if event.type == diacanvas.EVENT_2BUTTON_PRESS:
            self.edit()
            return True
        else:
            return ElementItem.on_event(self, event)

    def on_shape_iter(self):
        return iter([self._border, self._body])

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
