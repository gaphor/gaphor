#
# vim: sw=4

import gobject
import gtk

class ModelElementCellRenderer(gtk.CellRendererText):
    __gproperties__ = {
	'element':	(gobject.TYPE_PYOBJECT, 'element',
			 'Element to visualize in the cell',
			 gobject.PARAM_WRITABLE),
    }
    def __init__(self):
	self.__gobject_init__()

    def do_set_property (self, pspec, value):
	if pspec.name == 'element':
	    self.set_property ('text', element.name)
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	#if pspec.name == 'element':
	#else:
     	raise AttributeError, 'Unknown property %s' % pspec.name

gobject.type_register(ModelElementCellRenderer)

class TreeView:
    def __init__(self, treemodel):
	win = gtk.Window()
	win.set_title ('Tree view')

	win.set_default_size (200, 300)
	
	swin = gtk.ScrolledWindow ()
	swin.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	win.add (swin)

	view = gtk.TreeView (treemodel)

	def my_cell_renderer (column, cell, model, iter, data):
	    '''Custom cell renderer for the treeView. It should place an
	    image in cell[0] and the name in cell[1] as editable text.'''
	    assert len (column.get_cell_renderers()) == 2
	    rend = column.get_cell_renderers()
	    assert rend[0] is cell
	    value = model.get_value(iter, 0)
	    #print 'TESTFUNC:', rend, data
	    if value:
		rend[0].set_property('markup', '<b>' + 'M' + '</b>')
		rend[1].set_property('text', value)

	cell = gtk.CellRendererText ()
	#column = gtk.TreeViewColumn ('', cell, text=0)
	#view.append_column (column)
	#cell = ModelElementCellRenderer()
	column = gtk.TreeViewColumn ('', cell, text=0)
	column.set_cell_data_func (cell, my_cell_renderer, None)
	cell = gtk.CellRendererText ()
	cell.set_property ('editable', 1)
	column.pack_start (cell, 0)
	assert len (column.get_cell_renderers()) == 2
	view.append_column (column)
	swin.add (view)
	win.show_all ()

	self.window = win
	self.treeview = view
