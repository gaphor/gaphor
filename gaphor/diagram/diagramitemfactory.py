
# vim:sw=4:

import gobject
import gaphor.UML as UML

class DiagramItemFactory(object):
    """
    Factory class for creating diagram items.
    Normally one would access this class through by calling
    GaphorResource(gaphor.diagram.DiagramItemFactory)
    """
    __diagram2uml = { }

    def __init__(self):
	self.__index = 1

    def create (self, diagram, type, subject=None):
	"""
	Create a new diagram item. Items should not be created directly, but
	always through a factory.
	diagram is the diagram the item should be drawn on.
	type is the class of diagram item that is to be created
	subject is an objectal UML object that is to be connected to the
	new diagram item.
	"""
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
		factory = GaphorResource(UML.ElementFactory)
		subject = factory.create (uml_type)
		if issubclass (uml_type, UML.Namespace):
		    subject.namespace = diagram.namespace
		obj.set_property('subject', subject)
	return obj

    def set_next_id(self, id):
	"""
	set_next_id() sets the id to use for the next canvas item that will
	be created. This functionality should only be used when loading
	models from disk.
	"""
	if id > self.__index:
	    self.__index = id

    def flush(self):
	"""
	Reset the factory's state
	"""
	self.__index = 1

    def register(self, item_class, uml_class):
	"""
	Match a diagram item with a UML class. If a new item is to be created
	and no UML object is provided a new UML object will be created. This
	is typically used for ModelElement like elements. Relationships can
	exist without being bound to a UML object.
	"""
	DiagramItemFactory.__diagram2uml[item_class] = uml_class
