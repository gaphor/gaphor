# vim: sw=4
'''This is the TreeView that is most common (for example: it is used
in Rational Rose). This is a tree based on namespace relationships. As
a result only classifiers are shown here.
'''

import gtk
import gobject
import types
import UML

class NamespaceModel(gtk.GenericTreeModel):
    ''' The node is defined by a instance. We can reach the parent
        by <object>.namespace. The children can be found in the
	<object>.ownerElement list.'''

    def __unlink_cb(self):
        print 'Destroying model'

    def __destroy (self):
        print '__destroy'

    def __init__(self, model):
	if not isinstance (model, UML.Model):
	    raise AttributeError

	self.model = model;
	# Init parent:
	gtk.GenericTreeModel.__init__(self)
	self.set_property ('leak_references', gtk.FALSE);
	#self.connect ('dispose', self.__destroy)
	# TODO: connect to 'name' and 'unlink' and 'namespace' signal from
	#	the data objects.
	#	Removed signals when finalized.
	#	How can I notify views in a proper way if something changed.
    def dump(self):
        '''Dump the static structure of the model to stdout.'''
	def doit(node, depth):
	    print '|' + '   ' * depth + '"' + node.name + '" ' + str(node)
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
	print '************************************************************'
	print ' I\'m called at last!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
	return 0

    def on_get_n_columns(self):
	'''returns the number of columns in the model'''
	return 1

    def on_get_column_type(self, index):
	'''returns the type of a column in the model'''
	return gobject.TYPE_STRING

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
	print "on_get_path", node
	return node

    def on_get_iter(self, path):
        '''returns the node corresponding to the given path. The patch is a
	   tuple of values, like (0 1 1). We have to figure out a path that is
	   easy to use by on_get_value() and can also be easely extended by
	   on_iter_children() and chopped by on_iter_parent()'''
	node = self.model
	for n in path:
	    node = node.ownedElement[n]
	#print "on_get_iter", path, node
	return node

    def on_get_value(self, node, column):
	'''returns the value stored in a particular column for the node'''
	assert column == 0
	assert isinstance (node, UML.Namespace)
	#print "on_get_value", node.name
	return '<<' + str(node.__class__.__name__) + '>> ' + node.name

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
	parent = node.namespace
	index = parent.ownedElement.list.index (node)
	#print "on_iter_next", index
	try:
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

