'''
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import pango
import gobject
from diacanvas import CanvasText
from diagramitem import DiagramItem

class FeatureItem(CanvasText, DiagramItem):
    """
    FeatureItems are model elements who recide inside a ClassItem, such as
    methods and attributes. Those items can have comments attached, but only on
    the left and right side.
    Note that features can also be used inside objects.
    """
    __gproperties__ = {
	'subject':	(gobject.TYPE_PYOBJECT, 'subject',
			 'subject held by the relationship',
			 gobject.PARAM_READWRITE),
    }
    FONT='sans 10'

    def __init__(self):
	self.__gobject_init__()
	DiagramItem.__init__(self)
	diacanvas.CanvasText.__init__(self)
	font = pango.FontDescription(FeatureItem.FONT)
	self.set(font=font, width=self.width, alignment=pango.ALIGN_LEFT)
	w, h = self.__name.get_property('layout').get_pixel_size()
	self.set(height=h)
	self.connect('text_changed', self.on_text_changed)

    def do_set_property (self, pspec, value):
	if pspec.name == 'subject':
	    print 'Setting subject:', value
	    self._set_subject(value)
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'subject':
	    return self.subject
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name


#    def on_update(self, affine):
#	#ModelElementItem.on_update(self, affine)
#	pass

    def on_subject_update(self, name, old_value, new_value):
	if name == 'name':
	    self.set(text=self.subject.name)

    def on_text_changed(self, text_item, text):
	if text != self.subject.name:
	    self.subject.name = text

gobject.type_register(FeatureItem)
diacanvas.set_callbacks(FeatureItem)

