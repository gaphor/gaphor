"""ClassifierItem diagram item
"""
# vim:sw=4:et

import gobject
import pango
import diacanvas
from modelelement import ModelElementItem

class ClassifierItem(ModelElementItem, diacanvas.CanvasEditable):
    __gproperties__ = {
        'name': (gobject.TYPE_STRING, 'name', '', '', gobject.PARAM_READWRITE)
    }

    FONT='sans bold 10'

    def __init__(self, id=None):
        ModelElementItem.__init__(self, id)

        #self._name = diacanvas.CanvasText()
        #self.add_construction(self._name)
        #assert self._name != None
        #self._name = ''
        self._name = diacanvas.shape.Text()
        self._name.set_font_description(pango.FontDescription(ClassifierItem.FONT))
        self._name.set_alignment(pango.ALIGN_CENTER)
        #self._name.set(font=font, multiline=0,
        #                alignment=pango.ALIGN_CENTER)
        #self.connect('notify::subject', ClassifierItem.on_subject_notify)
        #self._name.connect('text-changed', self.on_text_changed)

    def postload(self):
        ModelElementItem.postload(self)
        # Set values in postload, since the load function doesn't send
        # notifications.
        #self._name.set_property('text', self.subject.name)
        #self._name = self.subject.name
        self._name.set_text(self._name)

    def do_set_property(self, pspec, value):
        if pspec.name == 'name':
            self.preserve_property('name')
            #self._name = value
            self.subject.name = value
            #self._name.set_text(value)
        else:
            ModelElementItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'name':
            #return self._name
            return self.subject.name
        else:
            return ModelElementItem.do_get_property(self, pspec)

    def get_name_size(self):
        """Return the width and height of the name shape.
        """
        return self._name.to_pango_layout(True).get_pixel_size()

    def update_name(self, x, y, width, height):
	self._name.set_pos((x, y))
	self._name.set_max_width(width)
	self._name.set_max_height(height)

    def postload(self):
        self._name.set_text(self.subject.name or '') #.set_property('text', self.subject.name)

    def on_subject_notify(self, pspec, notifiers=()):
        """See DiagramItem.on_subject_notify().
        """
        #log.info('ClassifierItem.on_subject_notify: %s' % str(notifiers))
        ModelElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)
        #self._name.set(text=self.subject and self.subject.name or '')
        self._name.set_text(self.subject and self.subject.name or '')

    def on_subject_notify__name(self, subject, pspec):
        assert self.subject is subject
        #print 'on_subject_notify__name: %s' % self.subject.name
        self._name.set_text(self.subject.name)
        self.request_update()

    # DiaCanvasItem callbacks:

    #def on_update(self, affine):
        #self.update_child(self._name, affine)
        #self._name.set_text(self._name or '')
        #ModelElementItem.on_update(self, affine)

    def on_event (self, event):
        if event.type == diacanvas.EVENT_2BUTTON_PRESS:
            self.start_editing(self._name)
            return True
        else:
            return ModelElementItem.on_event(self, event)

    def on_shape_iter(self):
        return iter([self._name])

    # Editable

    def on_editable_start_editing(self, shape):
        self.preserve_property('name')

    def on_editable_editing_done(self, shape, new_text):
        #assert shape is self._name
        self.preserve_property('name')
        if new_text != self.subject.name:
            self.subject.name = new_text
            #self._name = new_text
        #self._name.set_text(new_text)
        self.request_update()

gobject.type_register(ClassifierItem)
diacanvas.set_editable(ClassifierItem)

