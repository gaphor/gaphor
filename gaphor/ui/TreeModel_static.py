'''This is the TreeView that is most common (for example: it is used
in Rational Rose). This is a tree based on namespace relationships. As
a result only classifiers are shown here.
'''

import sys
sys.path.append ('..')

import gtk
import gobject
import types
import UML

# to create a new GtkTreeModel from python, you must derive from
# GenericTreeModel.
class TreeModel(gtk.GenericTreeModel):
    ''' The node is defined by a instance. We can reach the parent
        by <object>.namespace. The children can be found by the
	<object>.ownerElement list.'''

    def __init__(self, model):
	if not isinstance (model, UML.Model):
		raise AttributeError

	self.model = model;
	# Init parent:
	gtk.GenericTreeModel.__init__(self)

    def class_from_node(self, node):
        klass = self.klass
        for n in node:
	    attrdef = klass._attrdef[n]
	    klass = attrdef[1]
	return klass

    # the implementations for TreeModel methods are prefixed with on_
    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
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
	print "on_get_iter", path, node
	return node

    def on_get_value(self, node, column):
	'''returns the value stored in a particular column for the node'''
	assert column == 0
	assert isinstance (node, UML.Namespace)
	print "on_get_value", node.name
	return node.name

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
	parent = node.namespace
	index = parent.ownedElement.list.index (node)
	print "on_iter_next", index
	try:
		return parent.ownedElement[index + 1]
	except IndexError:
		return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
	return len (node.ownedElement) > 0

    def on_iter_children(self, node):
	'''returns the first child of this node'''
	return node.ownedElement[0]

    def on_iter_n_children(self, node):
	'''returns the number of children of this node'''
	return len (node.ownedElement) 

    def on_iter_nth_child(self, node, n):
	'''returns the nth child of this node'''
	print "on_iter_nth_child", node, n
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

def main():
    sys.path.append('../../tests')
    import CreateModel

    window = gtk.Window()
    window.connect('destroy', lambda win: gtk.main_quit())
    window.set_title('TreeView test')
    window.set_default_size(250, 400)

    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    window.add(scrolled_window)

    tree_model = TreeModel(CreateModel.model)
    tree_view = gtk.TreeView(tree_model)
    cell = gtk.CellRendererText()
    # the text in the column comes from column 0
    column = gtk.TreeViewColumn('', cell, text=0)
    tree_view.append_column(column)

    scrolled_window.add(tree_view)
    window.show_all()

    if __name__ == '__main__': gtk.main()

if __name__ == '__main__':
    main()
else:
    del main
