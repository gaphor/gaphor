'''
CommentItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import gobject
import pango

class CommentItem(ModelElementItem):
    EAR=15
    OFFSET=5
    FONT='sans 10'

    def __init__(self, id=None):
        ModelElementItem.__init__(self, id)
        self.set(min_width=CommentItem.EAR + 2 * CommentItem.OFFSET,
                 height=50, width=100)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)
        self._body = diacanvas.CanvasText()
        self.add_construction(self._body)
        font = pango.FontDescription(CommentItem.FONT)
        self._body.set(font=font, width=self.width - (CommentItem.OFFSET * 2),
                        alignment=pango.ALIGN_LEFT)
        self._body.move(CommentItem.OFFSET, CommentItem.OFFSET)
        self._body.connect('text_changed', self.on_text_changed)

    def postload(self):
        self._body.set(text=self.subject.body)

    def on_subject_notify(self, pspec):
        """See DiagramItem.on_subject_notify()."""
        ModelElementItem.on_subject_notify(self, pspec, ('body',))

        self._body.set(text=self.subject and self.subject.body or '')

    def on_subject_notify__name(self, subject, pspec):
        self._body.set(text=self.subject.body)

    def on_text_changed(self, text_item, text):
        if self.subject and text != self.subject.body:
            self.subject.body = text

    # DiaCanvasItem callbacks:

    def on_update(self, affine):
        # Outline the text, first tell the text how width it may become:
        self._body.set_property('width',
                        self.width - CommentItem.EAR - CommentItem.OFFSET)
        w, h = self._body.get_property('layout').get_pixel_size()
        self.set(min_height=h + CommentItem.OFFSET * 2)
        self._body.set_property('height', self.height - CommentItem.OFFSET * 2)
        self.update_child(self._body, affine)
        ModelElementItem.on_update(self, affine)

        # Width and height, adjusted for line width...
        w = self.width
        h = self.height
        ear = CommentItem.EAR
        self._border.line(((w - ear, 0), (w- ear, ear), (w, ear), (w - ear, 0),
                            (0, 0), (0, h), (w, h), (w, ear)))
        self.expand_bounds(1)

    def on_event (self, event):
        if event.type == diacanvas.EVENT_KEY_PRESS:
            self._body.focus()
            self._body.on_event(event)
            return True
        else:
            return ModelElementItem.on_event(self, event)

    def on_shape_iter(self):
        return iter([self._border])

    # Groupable

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        '''Do not allow the body to be removed.'''
        #self.emit_stop_by_name('remove')
        return 1

    def on_groupable_iter(self):
        return iter([self._body])

    def on_groupable_length(self):
        return 1

    def on_groupable_pos(self, item):
        if item == self._body:
            return 0
        else:
            return -1


gobject.type_register(CommentItem)
