#
# vim: sw=4

import gobject
import gtk
import gaphor.tree.namespace as namespace

class TreeView:
    def __init__(self, treemodel):
	win = gtk.Window()
	win.set_title ('Tree view')

	win.set_default_size (200, 300)
	
	swin = gtk.ScrolledWindow ()
	swin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	win.add (swin)

	#view = gtk.TreeView (treemodel)
	view = namespace.NamespaceView (treemodel)

#	def cell_renderer1 (column, cell, model, iter, data):
#	    value = model.get_value(iter, 0)
#	    name = value.__class__.__name__
#	    if len(name) > 0:
#		cell.set_property('markup', '<b>' + name[0] + '</b>')
#	    else:
#		cell.set_property('markup', '<b>?</b>')

#	def cell_renderer2 (column, cell, model, iter, data):
#	    value = model.get_value(iter, 0)
#	    name = value.name
#	    cell.set_property('text', name)
#
	#column = gtk.TreeViewColumn ('')
	#cell = gtk.CellRendererText ()
	#column.pack_start (cell, 0)
	#column.set_cell_data_func (cell, cell_renderer1, None)
	
	#cell = gtk.CellRendererText ()
	#cell.set_property ('editable', 1)
	#column.pack_start (cell, 0)
	#column.set_cell_data_func (cell, cell_renderer2, None)
	#assert len (column.get_cell_renderers()) == 2
	#view.append_column (column)
	swin.add (view)
	win.show_all ()

	self.window = win
	self.treeview = view
