#
# vim: sw=4

import gtk

class TreeView:
    def __init__(self, treemodel):
	win = gtk.Window()
	win.set_title ('Tree view')

	win.set_default_size (200, 300)
	
	swin = gtk.ScrolledWindow ()
	swin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	win.add (swin)

	view = gtk.TreeView (treemodel)
	cell = gtk.CellRendererText ()
	column = gtk.TreeViewColumn ('', cell, text=0)
	view.append_column (column)

	swin.add (view)
	win.show_all ()

	self.window = win
	self.treeview = view
