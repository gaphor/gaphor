
# vim:sw=4:

import gobject
import UML
from misc.singleton import Singleton

class DiagramItemFactory(Singleton):
    __diagram2uml = { }

    def init(self, *args, **kwargs):
	self.__index = 1

    def create (self, diagram, type, subject=None):
	obj = type()
	obj.set_property('id', self.__index)
	obj.set_property('parent', diagram.canvas.root)
	self.__index += 1
	uml_type = None
	if subject:
	    obj.set_property('subject', subject)
	elif DiagramItemFactory.__diagram2uml.has_key(type):
	    uml_type = DiagramItemFactory.__diagram2uml[type]
	    if uml_type:
		factory = UML.ElementFactory()
		subject = factory.create (uml_type)
		if issubclass (uml_type, UML.Namespace):
		    subject.namespace = diagram.namespace
		obj.set_property('subject', subject)
	return obj

    def register(self, item_class, uml_class):
	gobject.type_register(item_class)
	DiagramItemFactory.__diagram2uml[item_class] = uml_class
