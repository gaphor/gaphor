#!/usr/bin/env python
'''This application shows a nice tree view of the UML meta model.

Somehow, this peace of code seems to crash by X server. I thinnk it's a bug in
GTK+. ... but how do I isolate the bug?
'''

import sys
sys.path.append("../gaphor")

import gtk
import gobject
import types

from UML import *

# to create a new GtkTreeModel from python, you must derive from
# GenericTreeModel.
class TreeModel(gtk.GenericTreeModel):
    ''' The node is defined by a "name" tuple. '''

    def __init__(self, klass):
	'''constructor for the model.  Make sure you call
	PyTreeModel.__init__'''
	self.iter = None # Value used to keep track of iterations.
	self.klass = klass;
	
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
	def get_iter(klass, path):
	    item = klass._attrdef.items()[path[0]]
	    if len(path) == 1:
		return (item[0],)
	    else:
	        subklass = klass._attrdef.items()[path[0]][1][1]
		return (item[0],) + get_iter(subklass, path[1:])
	
        node = get_iter(self.klass, path)
	
	#print "on_get_iter", path, node
	return node

    def on_get_value(self, node, column):
	'''returns the value stored in a particular column for the node'''
	assert column == 0
	attr = node[-1]
	parent = self.class_from_node(node[:-1])
	attrdef = parent._attrdef[attr]
	#print "on_get_value", node, attrdef
	closing = ")"
	if attrdef[0] == Sequence:
	    closing = "*)"
	    
	if len(attrdef) == 3:
	    return attr + " (" + attrdef[1].__name__ + "::" + attrdef[2] + closing
	else:
	    return attr + " (" + attrdef[1].__name__ + closing

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
	attr = node[-1]
	parent = self.class_from_node(node[:-1])
	attrdef = parent._attrdef[attr]
	items = parent._attrdef.items()
	sentinel = 0
	for i in items:
	    if sentinel:
	        node = node[:-1] + (i[0],)
		#print "on_iter_next", node
		return node
	    elif i[0] == attr:
	        sentinel = 1 # Use next item
	#print "on_iter_next (None)"
        return None

    def on_iter_children(self, node):
	'''returns the first child of this node'''
	klass = self.class_from_node(node)
	if klass.__dict__.has_key("_attrdef"):
	    item = klass._attrdef.items()[0][0]
	    #print "on_iter_children", node, item
	    return node + (item,)
	else:
	    #print "on_iter_children (None)"
	    return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
	#return 0
	klass = self.class_from_node(node)
	#print "on_iter_has_child", node
	return klass.__dict__.has_key("_attrdef") and len(klass._attrdef) > 0

    def on_iter_n_children(self, node):
	'''returns the number of children of this node'''
	klass = self.class_from_node(node)
	if klass.__dict__.has_key("_attrdef"):
	    items = klass._attrdef.items()
	    #print "on_iter_n_children", len(items)
	    return len(items) - 1
	else:
	    #print "on_iter_n_children (None)"
	    return 0

    def on_iter_nth_child(self, node, n):
	'''returns the nth child of this node'''
	#print "on_iter_nth_child"
        if node == None:
	    #print 'result =', n, self.klass._attrdef.items()[0][0]
            return (self.klass._attrdef.items()[0][0],)
        klass = self.class_from_node(node)
	if klass.__dict__.has_key("_attrdef") and len(node) >= n:
	    item = klass._attrdef.items()[n][0]
	    #print "on_iter_nth_child", node, klass.__name__, item
	    #print 'result =', n, node, item
	    return node + (item,)
	else:
	    #print 'result =', n, None
	    return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
	#print "on_iter_parent", node
	return node[:-1]

def main():
    args = sys.argv[1:]
    
    base_class = None
    try:
        base_class = eval(args[0])
    except NameError:
        print "Invalid class name (" + args[0] + ")"
        sys.exit(1)
    except IndexError:
	print "Use gbrowseUML.py <class>, now using class ModelElement"
	base_class = ModelElement

    window = gtk.Window()
    window.connect('destroy', lambda win: gtk.main_quit())
    window.set_title('gbrowseUML -- ' + base_class.__name__)
    window.set_default_size(250, 400)

    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    window.add(scrolled_window)

    model = TreeModel(base_class)
    tree_view = gtk.TreeView(model)
    cell = gtk.CellRendererText()
    # the text in the column comes from column 0
    column = gtk.TreeViewColumn(base_class.__name__, cell, text=0)
    tree_view.append_column(column)

    scrolled_window.add(tree_view)
    window.show_all()

    gtk.main()

if __name__ == '__main__':
    main()
else:
    del main
