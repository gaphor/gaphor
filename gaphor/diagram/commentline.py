'''
CommentLine -- A line that connects a comment to another model element.
'''
# vim:sw=4

import gobject
import diacanvas
import UML

class CommentLineItem(diacanvas.CanvasLine):
    __gproperties__ = {
	'id':		(gobject.TYPE_PYOBJECT, 'id',
			 'Identification number of the canvas item',
			 gobject.PARAM_READWRITE),
    }
    __savable_properties = [ 'affine', 'line_width',
			'color', 'cap', 'join', 'orthogonal', 'horizontal' ]
    def __init__(self):
	self.__gobject_init__()
	self.__id = -1
	self.set_property('dash', (7.0, 5.0))

    def save (self, store):
	for prop in CommentLineItem.__savable_properties:
	    store.save_property(prop)
	points = [ ]
	for h in self.handles:
	    pos = h.get_property ('pos_i')
	    #print 'pos:', pos
	    points.append (pos)
	store.save_attribute ('points', points)
	c = self.handles[0].connected_to
	if c:
	    store.save_attribute ('head_connection', c.get_property('id'))
	c = self.handles[-1].connected_to
	if c:
	    store.save_attribute ('tail_connection', c.get_property('id'))

    def load (self, store):
	for prop in CommentLineItem.__savable_properties:
	    self.set_property(prop, eval (store.value(prop)))


    def do_set_property (self, pspec, value):
	if pspec.name == 'id':
	    print self, 'id', value
	    self.__id = int(value)
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'id':
	    return self.__id
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def on_connect_handle(self, handle):
	"""No connections are allows to the CommentLine.
	"""
	#ret = diacanvas.CanvasLine.on_connect_handle(handle)
	return 0

    def on_disconnect_handle(self, handle):
	"""No connections are allows to the CommentLine.
	"""
	#ret = diacanvas.CanvasLine.on_disconnect_handle(handle)
	return 0

    # Gaphor Connection Protocol

    def allow_connect_handle(self, handle, connecting_to):
	"""
	This method is called by a canvas item if the user tries to connect
	this object's handle. allow_connect_handle() checks if the line is
	allowed to be connected. In this case that means that one end of the
	line should be connected to a Comment.
	Returns: TRUE if connection is allowed, FALSE otherwise.
	"""
	h = self.handles
	c1 = h[0].connected_to
	c2 = h[-1].connected_to
	# OK if both sides are not connected yet.
	if not c1 and not c2:
	    return 1
	
	if handle is h[0]:
	    c1 = connecting_to
	elif handle is h[-1]:
	    c2 = connecting_to
	else:
	    raise AttributeError, 'handle should be the first or the last handle of the CommentLine'

	# We should not connect if both ends will become a Comment
	if isinstance(c1.subject, UML.Comment) and \
		isinstance(c2.subject, UML.Comment):
	    return 0
	# Also do not connect if both ends are non-Comments
	if not isinstance(c1.subject, UML.Comment) and \
		not isinstance(c2.subject, UML.Comment):
	    return 0

	# Allow connection
	return 1

    def confirm_connect_handle (self, handle):
	"""
	This method is called after a connection is established. This method
	sets the internal state of the line and updates the data model.
	"""
	print 'confirm_connect_handle', handle
	c1 = self.handles[0].connected_to
	c2 = self.handles[-1].connected_to
	if c1 and c2:
	    s1 = c1.subject
	    s2 = c2.subject
	    if isinstance (s1, UML.Comment):
		s1.annotatedElement = s2
	    elif isinstance (s2, UML.Comment):
		s2.annotatedElement = s1
	    else:
		raise TypeError, 'One end of the CommentLine should connect to a Comment'

    def allow_disconnect_handle (self, handle):
	return 1

    def confirm_disconnect_handle (self, handle, was_connected_to):
	print 'confirm_disconnect_handle', handle
	c1 = None
	c2 = None
	if handle is self.handles[0]:
	    c1 = was_connected_to
	    c2 = self.handles[-1].connected_to
	elif handle is self.handles[-1]:
	    c1 = self.handles[0].connected_to
	    c2 = was_connected_to
	
	if c1 and c2:
	    s1 = c1.subject
	    s2 = c2.subject
	    if isinstance (s1, UML.Comment):
		del s1.annotatedElement[s2]
	    elif isinstance (s2, UML.Comment):
		del s2.annotatedElement[s1]
	    else:
		raise TypeError, 'One end of the CommentLine should connect to a Comment. How could this connect anyway?'

gobject.type_register(CommentLineItem)
diacanvas.set_callbacks(CommentLineItem)
