# vim: sw=4

import UML
import diagram
import diacanvas
import types

class Storage(object):
    VALUE='Value'
    ELEMENT='Element'
    CANVAS='Canvas'
    REFERENCE='Reference'
    CANVAS_ITEM='CanvasItem'
    NAME='name'
    TYPE='type'
    ID='id'
    CID='cid'
    REFID='refid'
    PVALUE='value'

    def __init__(self, factory, ns, node, obj=None):
	object.__init__(self)
	self.__factory = factory
	self.__ns = ns
	self.__node = node
	self.__obj = obj

    def new(self, obj):
	node = None
	if isinstance (obj, UML.Element):
	    node = self.__node.newChild (self.__ns, Storage.ELEMENT, None)
	    node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setProp (Storage.ID, 'a' + str (obj.id))
	elif isinstance (obj, diacanvas.Canvas):
	    node = self.__node.newChild (self.__ns, Storage.CANVAS, None)
	elif isinstance (obj, diacanvas.CanvasItem):
	    node = self.__node.newChild (self.__ns, Storage.CANVAS_ITEM, None)
	    node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setProp (Storage.CID, str (obj)[-9:-1])
	return Storage (self.__factory, self.__ns, node, obj)

    def save_property (self, prop):
	prop_val = repr (self.__obj.get_property (prop))
	self.save (prop, prop_val)

    def save (self, name, obj):
	print 'saving', name, obj
	if isinstance (obj, UML.Element):
	    node = self.__node.newChild (self.__ns, Storage.REFERENCE, None)
	    node.setProp (self.NAME, name)
	    node.setProp (self.REFID, 'a' + str(obj.id))
	else:
	    data = None
	    if isinstance (obj, types.IntType) or \
		    isinstance (obj, types.LongType) or \
		    isinstance (obj, types.FloatType):
		data = str(obj)
	    elif isinstance (obj, types.StringType):
		data = str(obj)
	    if data:
		node = self.__node.newChild (self.__ns, Storage.VALUE, None)
		node.setProp (Storage.NAME, name)
		node.setProp (Storage.PVALUE, data)

