'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4

import gobject
import diacanvas
import UML
from diagramitem import DiagramItem

class RelationshipItem(diacanvas.CanvasLine, DiagramItem):
    __gproperties__ = {
	'id':		(gobject.TYPE_PYOBJECT, 'id',
			 'Identification number of the canvas item',
			 gobject.PARAM_READWRITE),
	'subject':	(gobject.TYPE_PYOBJECT, 'subject',
			 'subject held by the relationship',
			 gobject.PARAM_READWRITE),
    }
    __savable_properties = [ 'affine', 'line_width',
			'color', 'cap', 'join', 'orthogonal', 'horizontal' ]
    def __init__(self):
	self.__gobject_init__()
	DiagramItem.__init__(self)
	self.subject = None
	self.__id = -1

    def save (self, store):
	for prop in RelationshipItem.__savable_properties:
	    store.save_property(prop)
	points = [ ]
	for h in self.handles:
	    pos = h.get_pos_i ()
	    #print 'pos:', pos, h.get_property('pos_i')
	    points.append (pos)
	store.save_attribute ('points', points)
	c = self.handles[0].connected_to
	if c:
	    store.save_attribute ('head_connection', c)
	c = self.handles[-1].connected_to
	if c:
	    store.save_attribute ('tail_connection', c)
	if self.subject:
	    store.save_attribute('subject', self.subject)

    def load (self, store):
	for prop in RelationshipItem.__savable_properties:
	    self.set_property(prop, eval (store.value(prop)))
	points = eval(store.value('points'))
	assert len(points) >= 2
	self.set_property('head_pos', points[0])
	self.set_property('tail_pos', points[1])
	for p in points[2:]:
	    item.set_property ('add_point', p)
	# Subject may have been omited.
	try:
	    subject = store.reference('subject')
	    assert len(subject) == 1
	    self._set_subject(subject[0])
	except ValueError:
	    pass

    def postload(self, store):
	for name, refs in store.references().items():
	    if name == 'head_connection':
		assert len(refs) == 1
		refs[0].connect_handle (self.handles[0])
	    elif name == 'tail_connection':
		assert len(refs) == 1
		refs[0].connect_handle (self.handles[-1])

    def do_set_property (self, pspec, value):
	if pspec.name == 'id':
	    print self, 'id', value
	    self.__id = int(value)
	elif pspec.name == 'subject':
	    print 'Setting subject:', value
	    self._set_subject(value)
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'id':
	    return self.__id
	elif pspec.name == 'subject':
	    return self.subject
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def on_glue(self, handle, wx, wy):
	return self._on_glue(handle, wx, wy, diacanvas.CanvasLine)

    def on_connect_handle (self, handle):
	return self._on_connect_handle(handle, diacanvas.CanvasLine)

    def on_disconnect_handle (self, handle):
	return self._on_disconnect_handle(handle, diacanvas.CanvasLine)

    # Gaphor Connection Protocol
    #
    # The item a handle is connecting to is in charge of the connection
    # cyclus. However it informs the item it is connecting to by means of
    # the four methods defined below. The items that are trying to connect
    # (mostly Relationship objects or CommentLines) know what kind of item
    # they are allowed to connect to.

    def allow_connect_handle(self, handle, connecting_to):
	"""
	This method is called by a canvas item if the user tries to connect
	this object's handle. allow_connect_handle() checks if the line is
	allowed to be connected. In this case that means that one end of the
	line should be connected to a Relationship.
	Returns: TRUE if connection is allowed, FALSE otherwise.
	"""
	return 0

    def confirm_connect_handle (self, handle):
	"""
	This method is called after a connection is established. This method
	sets the internal state of the line and updates the data model.
	"""
	pass

    def allow_disconnect_handle (self, handle):
	"""
	If a handle wants to disconnect, this method is called first. This
	method is here mainly for the sake of completeness, since it is
	quite unlikely that a handle is not allowed to disconnect.
	"""
	return 1

    def confirm_disconnect_handle (self, handle, was_connected_to):
	"""
	This method is called to do some cleanup after 'self' has been
	disconnected from 'was_connected_to'.
	"""
	pass


gobject.type_register(RelationshipItem)
diacanvas.set_callbacks(RelationshipItem)
