# vim: sw=4
"""This is the TreeView that is most common (for example: it is used
in Rational Rose). This is a tree based on namespace relationships. As
a result only classifiers are shown here.
"""

import gtk
import gobject
import types
import UML
import sys

class NamespaceModel(gtk.GenericTreeModel):
    """
    The node is defined by a instance. We can reach the parent
    by <object>.namespace. The children can be found in the
    <object>.ownerElement list.
    """

    def __element_signals (self, key, obj):
	if key == 'name':
	    path = self.get_path (obj)
	    if path != ():
		# During loading, the item may be connected, but is not
		# in the tree path (ie. the namespace is not set).
		iter = self.get_iter (path)
		self.row_changed (path,  iter)
        elif key == 'namespace' and obj.namespace:
	    path = self.get_path(obj)
	    iter = self.get_iter(path)
	    print 'Namespace set for', obj, path
	    self.row_inserted (path, iter)
	elif key == '__unlink__':
	    print 'Destroying', obj

    def __factory_signals (self, key, obj, factory):
        if key == 'create' and isinstance (obj, UML.Namespace):
	    print 'Object added'
	    obj.connect (self.__element_signals, obj)
	    if obj.id == 1:
		self.model = obj
	    try:
		if obj.namespace:
		     path = self.get_path(obj)
		     iter = self.get_iter(path)
		     self.row_inserted (path, iter)
	    except AttributeError:
		pass
	elif key == 'remove' and isinstance (obj, UML.Namespace):
	    if obj is self.model:
		for n in obj.ownedElement.list:
		    self.row_deleted((0,))
	    else:
		path = self.get_path (obj)
		print 'Removing object', obj, path
		self.row_deleted (path)
	    obj.disconnect (self.__element_signals)

    def __init__(self, factory):
	if not isinstance (factory, UML.ElementFactory):
	    raise AttributeError

	self.model = factory.lookup(1);
	#print "self.model =", self.model
	# Init parent:
	gtk.GenericTreeModel.__init__(self)
	# We own the references to the iterators.
	self.set_property ('leak_references', 0)

	#self.factory == UML.ElementFactory()
	factory.connect (self.__factory_signals, factory)
	#del self.factory

	# Set signals to all Namespace objects in the factory:
	for element in factory.values():
	    if isinstance (element, UML.Namespace):
		element.connect (self.__element_signals, element)
 
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
	levels) for a particular node.'''
	def to_path (n):
	    #print 'Fetching', n
	    if n.namespace:
	        #print '...from', n.namespace.ownedElement.list
		
	        return (n.namespace.ownedElement.index(n),) + \
			to_path (n.namespace)
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
	    index = parent.ownedElement.list.index (node)
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

    def __init__(self, model):
	assert isinstance (model, NamespaceModel)
	self.__gobject_init__()
	gtk.TreeView.__init__(self, model)

	column = gtk.TreeViewColumn ('')
	# First cell in the column is for an image...
	cell = gtk.CellRendererText ()
	column.pack_start (cell, 0)
	column.set_cell_data_func (cell, self._set_pixbuf, None)
	
	# Second cell if for the name of the object...
	cell = gtk.CellRendererText ()
	cell.set_property ('editable', 1)
	column.pack_start (cell, 0)
	column.set_cell_data_func (cell, self._set_name, None)
	# TODO: Add handler to set text if editing is done.
	assert len (column.get_cell_renderers()) == 2
	self.append_column (column)

    def _set_pixbuf (self, column, cell, model, iter, data):
	value = model.get_value(iter, 0)
	name = value.__class__.__name__
	if len(name) > 0:
	    cell.set_property('markup', '[<b>' + name[0] + '</b>]')
	else:
	    cell.set_property('markup', '[<b>?</b>]')

    def _set_name (self, column, cell, model, iter, data):
	value = model.get_value(iter, 0)
	name = value.name
	cell.set_property('text', name)

gobject.type_register(NamespaceView)
