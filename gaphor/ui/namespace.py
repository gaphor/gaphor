# vim: sw=4
"""This is the TreeView that is most common (for example: it is used
in Rational Rose). This is a tree based on namespace relationships. As
a result only classifiers are shown here.
"""

import gtk
import gobject
import types
import gaphor.UML as UML
import sys
import string
import stock

class NamespaceModel(gtk.GenericTreeModel):
    """
    The node is defined by a instance. We can reach the parent
    by <object>.namespace. The children can be found in the
    <object>.ownerElement list.
    """

    def __init__(self, factory):
	if not isinstance (factory, UML.ElementFactory):
	    raise AttributeError

	self.model = None
	for e in factory.values():
	    if isinstance(e, UML.Model):
		self.model = e
		break
	#self.model = factory.lookup(1);
	# Init parent:
	gtk.GenericTreeModel.__init__(self)
	# We own the references to the iterators.
	self.set_property ('leak_references', 0)

	factory.connect (self.__factory_signals, factory)

	# Set signals to all Namespace objects in the factory:
	for element in factory.values():
	    if isinstance (element, UML.Namespace):
		element.connect (self.__element_signals, element)
 
    def __element_signals (self, key, old_value, new_value, obj):
	if key == 'name':
	    path = self.get_path (obj)
	    if path != ():
		# During loading, the item may be connected, but is not
		# in the tree path (ie. the namespace is not set).
		iter = self.get_iter(path)
		self.row_changed(path, iter)
	elif key == 'ownedElement' and old_value == 'add':
	    def recursive_add(element):
		path = self.get_path(element)
		#print 'ownedElement ADD', element, element.namespace, path
		iter = self.get_iter(path)
		self.row_inserted(path, iter)
		for child in element.ownedElement:
		    recursive_add(child)
	    recursive_add(new_value)
	elif key == 'ownedElement' and old_value == 'remove':
	    path = self.get_path(new_value)
	    log.debug( 'ownedElement remove: %s %s %s' % (old_value, new_value, path))
	    if path != ():
		self.row_deleted(path)
	elif key == '__unlink__':
	    pass # Stuff is handled in namespace and ownedElement keys...
	    #print 'Destroying', obj

    def __factory_signals (self, key, obj, factory):
        if key == 'create' and isinstance (obj, UML.Namespace):
	    obj.connect (self.__element_signals, obj)
	    if isinstance(obj, UML.Model): #obj.id == 1:
		self.model = obj
	elif key == 'remove' and isinstance (obj, UML.Namespace):
	    if obj is self.model:
		for n in obj.ownedElement:
		    self.row_deleted((0,))
	    obj.disconnect (self.__element_signals)

    def dump(self):
        '''Dump the static structure of the model to stdout.'''
	def doit(node, depth):
	    print '|' + '   ' * depth + '"' + node.name + '" ' + str(node) + \
		    str(self.on_get_path(node)) + '  ' + str(sys.getrefcount(node))
	    if self.on_iter_has_child (node):
		iter = self.on_iter_children (node)
		while iter != None:
		    #print 'iter:', iter, depth
		    doit (iter, depth + 1)
		    iter = self.on_iter_next (iter)

	doit (self.model, 0)

    def class_from_node(self, node):
        klass = self.klass
        for n in node:
	    attrdef = klass._attrdef[n]
	    klass = attrdef[1]
	return klass

    # the implementations for TreeModel methods are prefixed with on_
    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	#print '************************************************************'
	#print ' I\'m called at last!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
	return 0

    def on_get_n_columns(self):
	'''returns the number of columns in the model'''
	return 1

    def on_get_column_type(self, index):
	'''returns the type of a column in the model'''
	#return gobject.TYPE_STRING
	return gobject.TYPE_PYOBJECT

    def get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node. This is done in reverse order, so the
	root path will become first.'''
	assert isinstance (node, UML.Element)
	def to_path (n):
	    ns = n.namespace
	    if ns:
	        return to_path(ns) + (ns.ownedElement.index(n),)
	    else:
	        return ()
	#print "on_get_path", node
	return to_path (node)

    def on_get_path (self, node):
        return self.get_path (node)

    def on_get_iter(self, path):
        '''returns the node corresponding to the given path. The patch is a
	   tuple of values, like (0 1 1). We have to figure out a path that is
	   easy to use by on_get_value() and can also be easely extended by
	   on_iter_children() and chopped by on_iter_parent()'''
	#print 'Namespace.on_get_iter():', path
	node = self.model
	try:
	    if node:
		for n in path:
		    node = node.ownedElement[n]
	except IndexError, e:
	    print 'No path %s to a node' % str(path)
	    return None
	#print "on_get_iter", path, node
	return node

    def on_get_value(self, node, column):
	'''returns the model element that matches 'node'.'''
	assert column == 0
	assert isinstance (node, UML.Namespace)
	#print "on_get_value", node.name
	#if column == 0:
	#    return '[' + str(node.__class__.__name__)[0] + ']'
	#else:
	#    return node.name
	#return node.name
	return node
	#return ( '[' + str(node.__class__.__name__)[0] + '] ', node.name )

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
	#print 'on_iter_next:', node, node.namespace
	parent = node.namespace
	if not parent:
	    return None
	#print "on_iter_next", index
	try:
	    index = parent.ownedElement.index (node)
	    return parent.ownedElement[index + 1]
	except IndexError:
	    return None
	
    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
	#print 'on_iter_has_child', node
	return len (node.ownedElement) > 0

    def on_iter_children(self, node):
	'''returns the first child of this node'''
	#print 'on_iter_children'
	return node.ownedElement[0]

    def on_iter_n_children(self, node):
	'''returns the number of children of this node'''
	#print 'on_iter_n_children'
	return len (node.ownedElement) 

    def on_iter_nth_child(self, node, n):
	'''returns the nth child of this node'''
	#print "on_iter_nth_child", node, n
	if node is None:
	    return self.model
	try:
	    return node.ownedElement[n]
	except IndexError:
	    return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
	#print "on_iter_parent", node
	return node.namespace


class NamespaceView(gtk.TreeView):
    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
	('STRING', 0, TARGET_STRING),
	('text/plain', 0, TARGET_STRING),
	('gaphor/element-id', 0, TARGET_ELEMENT_ID)]
    # Can not set signals for some reason...
#    __gsignals__ = { 'drag_begin': 'override',
#    		     'drag_data_get': 'override',
#    		     'drag_data_delete': 'override',
#		     'drag_data_received': 'override' }

    def __init__(self, model):
	assert isinstance (model, NamespaceModel), 'model is not a NamespaceModel (%s)' % str(model)
	self.__gobject_init__()
	gtk.TreeView.__init__(self, model)
	self.set_property('headers-visible', 0)
	self.set_rules_hint(gtk.TRUE)
	selection = self.get_selection()
	selection.set_mode(gtk.SELECTION_BROWSE)
	column = gtk.TreeViewColumn ('')
	# First cell in the column is for an image...
	cell = gtk.CellRendererPixbuf ()
	column.pack_start (cell, 0)
	column.set_cell_data_func (cell, self._set_pixbuf, None)
	
	# Second cell if for the name of the object...
	cell = gtk.CellRendererText ()
	#cell.set_property ('editable', 1)
	cell.connect('edited', self._name_edited)
	column.pack_start (cell, 0)
	column.set_cell_data_func (cell, self._set_name, None)

	assert len (column.get_cell_renderers()) == 2
	self.append_column (column)

	# DND info:
	# drag
	self.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
			     NamespaceView.DND_TARGETS,
			     gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)
	#self.connect('drag_begin', NamespaceView.do_drag_begin)
	self.connect('drag_data_get', NamespaceView.do_drag_data_get)
	#self.connect('drag_data_delete', NamespaceView.do_drag_data_delete)
	# drop
	#self.drag_dest_set (gtk.DEST_DEFAULT_ALL, NamespaceView.DND_TARGETS[:-1],
	#		    gtk.gdk.ACTION_COPY)
	#self.connect('drag_data_received', NamespaceView.do_drag_data_received)
	#self.connect('drag_motion', NamespaceView.do_drag_motion)
	#self.connect('drag_drop', NamespaceView.do_drag_drop)

    def _set_pixbuf (self, column, cell, model, iter, data):
	value = model.get_value(iter, 0)
	stock_id = stock.get_stock_id(value.__class__)
	if stock_id:
	    icon = self.render_icon (stock_id, gtk.ICON_SIZE_MENU, '')
	    cell.set_property('pixbuf', icon)

    def _set_name (self, column, cell, model, iter, data):
	value = model.get_value(iter, 0)
	name = string.replace(value.name, '\n', ' ')
	cell.set_property('text', name)

    def _name_edited (self, cell, path_str, new_text):
	"""
	The text has been edited. This method updates the data object.
	Note that 'path_str' is a string where the fields are separated by
	colons ':', like this: '0:1:1'. We first turn them into a tuple.
	"""
	path_list = path_str.split(':')
	path = ()
	for p in path_list:
	    path = path + (int(p),)
	model = self.get_property('model')
	iter = model.get_iter(path)
	element = model.get_value(iter, 0)
	element.name = new_text

#    def do_drag_begin (self, context):
#	print 'do_drag_begin'

    def do_drag_data_get (self, context, selection_data, info, time):
	print 'do_drag_data_get'
	selection = self.get_selection()
	model, iter = selection.get_selected()
	if iter:
	    element = model.get_value (iter, 0)
	    if info == NamespaceView.TARGET_ELEMENT_ID:
		selection_data.set(selection_data.target, 8, str(element.id))
	    else:
		selection_data.set(selection_data.target, 8, element.name)

    def do_drag_data_delete (self, context, data):
	print 'Delete the data!'

    # Drop
    def do_drag_motion(self, context, x, y, time):
	print 'drag_motion', x, y
	return 1
   
    def do_drag_data_received(self, w, context, x, y, data, info, time):
	print 'drag_data_received'
        if data and data.format == 8:
	    print 'drag_data_received:', data.data
	    context.finish(gtk.TRUE, gtk.FALSE, time)
	else:
	    context.finish(gtk.FALSE, gtk.FALSE, time)
	gobject.emit_stop_by_name('drag_data_received')

    def do_drag_drop(self, context, x, y, time):
	print 'drag_drop'
	return 1

gobject.type_register(NamespaceModel)
gobject.type_register(NamespaceView)
