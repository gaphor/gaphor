'''
CommentLine -- A line that connects a comment to another model element.

TODO: Why do we lose the __id property when we do a get_property after a model
has been loaded. It works okay when creating new items.
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor.UML as UML

class CommentLineItem(diacanvas.CanvasLine):
    __gproperties__ = {
	'id':		(gobject.TYPE_PYOBJECT, 'id',
			 'Identification number of the canvas item',
			 gobject.PARAM_READWRITE),
    }
    __savable_properties = [ 'affine', 'line_width',
			'color', 'cap', 'join', 'orthogonal', 'horizontal' ]
    def __init__(self):
	diacanvas.CanvasLine.__init__(self)
	self.__gobject_init__()
	self.__id = None
	self.__shape = None
	self.set_property('dash', (7.0, 5.0))

    def set_id(self, value):
	self.__id = value

    def save (self, save_func):
	for prop in CommentLineItem.__savable_properties:
	    save_func(prop, self.get_property(prop))
	points = [ ]
	for h in self.handles:
	    pos = h.get_pos_i ()
	    points.append (pos)
	save_func('points', points)
	c = self.handles[0].connected_to
	if c:
	    save_func('head_connection', c)
	c = self.handles[-1].connected_to
	if c:
	    save_func ('tail_connection', c)

    def load (self, name, value):
	if name == 'points':
	    points = eval(value)
	    self.set_property('head_pos', points[0])
	    self.set_property('tail_pos', points[1])
	    for p in points[2:]:
		item.set_property ('add_point', p)
	elif name == 'head_connection':
	    self._load_head_connection = value
	elif name == 'tail_connection':
	    self._load_tail_connection = value
	else:
	    self.set_property(name, eval(value))

    def postload(self):
	if hasattr(self, '_load_head_connection'):
	    self._load_head_connection.connect_handle (self.handles[0])
	    del self._load_head_connection
	if hasattr(self, '_load_tail_connection'):
	    self._load_tail_connection.connect_handle (self.handles[-1])
	    del self._load_tail_connection

    def do_set_property (self, pspec, value):
	if pspec.name == 'id':
	    #self.__id = value
	    self.set_data('id', value)
	    #print self, '__id', self.__dict__
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'id':
	    return self.get_data('id')

	    #print self, 'get_property(id)', self.__dict__
	    if not hasattr(self, '_CommentLineItem__id'):
		log.warning('No ID found, generating a new one...')
		import gaphor.misc.uniqueid as uniqueid
		self.__id = uniqueid.generate_id()
	    return self.__id
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def on_glue(self, handle, wx, wy):
	"No connections are allowed on a CommentLine."
	return None

    def on_connect_handle(self, handle):
	"No connections are allows to the CommentLine."
	return 0

    def on_disconnect_handle(self, handle):
	"No connections are allows to the CommentLine."
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
	#print 'confirm_connect_handle', handle
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
	#print 'confirm_disconnect_handle', handle
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

