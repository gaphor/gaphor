'''
ClassifierItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import pango
import gobject
import sys

class ClassifierItem(ModelElementItem):
    FONT='sans bold 10'

    def __init__(self, id=None):
	ModelElementItem.__init__(self, id)

	self._name = diacanvas.CanvasText()
	self.add_construction(self._name)
	assert self._name != None
	font = pango.FontDescription(ClassifierItem.FONT)
	self._name.set(font=font, multiline=0,
			alignment=pango.ALIGN_CENTER)
	self.connect('notify::subject', ClassifierItem.on_subject_notify)
	self._name.connect('text_changed', self.on_text_changed)
	self.subject_name_changed_id = None

    def on_subject_notify(self, pspec):
	"""A new subject is set on this model element.
	"""
	if self.subject_name_changed_id:
	    self.subject_name_changed_id[0].disconnect(self.subject_name_changed_id[1])
	    self.subject_name_changed_id = None
	if self.subject:
	    self.subject_name_changed_id = (self.subject, self.subject.connect('name', self.on_subject_name_changed))
	self._name.set(text=self.subject and self.subject.name or '')
	self.request_update()

    def on_subject_name_changed(self, subject, pspec):
	assert self.subject is subject
	self._name.set(text=self.subject.name)

    def on_text_changed(self, text_item, text):
	if self.subject and text != self.subject.name:
	    self.subject.name = text

    # DiaCanvasItem callbacks:

    def on_update(self, affine):
	self.update_child(self._name, affine)
	ModelElementItem.on_update(self, affine)

    def on_event (self, event):
	if event.type == diacanvas.EVENT_KEY_PRESS:
	    self._name.focus()
	    self._name.on_event (event)
	    return True
	else:
	    return ModelElementItem.on_event(self, event)

    # Groupable

    def on_groupable_add(self, item):
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the name to be removed.'''
	return 1

    def on_groupable_iter(self):
	return iter([self._name])

    def on_groupable_length(self):
	return 1

    def on_groupable_pos(self, item):
	if item == self._name:
	    return 0
	else:
	    return -1


gobject.type_register(ClassifierItem)
