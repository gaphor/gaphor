
import UML, gtk
from tree.namespace import *

import CreateModel

window = gtk.Window()
window.connect('destroy', lambda win: gtk.main_quit())
window.set_title('TreeView test')
window.set_default_size(250, 400)

scrolled_window = gtk.ScrolledWindow()
scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
window.add(scrolled_window)

tree_model = NamespaceModel(CreateModel.model)

tree_view = gtk.TreeView(tree_model)
cell = gtk.CellRendererText()
# the text in the column comes from column 0
column = gtk.TreeViewColumn('', cell, text=0)
tree_view.append_column(column)

scrolled_window.add(tree_view)
window.show_all()

tree_model.dump()

gtk.main()

tree_model.dump()
