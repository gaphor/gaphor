
# vim:sw=4

import gtk
import namespace
import gaphor.UML as UML
from abstractwindow import AbstractWindow

class MainWindow(AbstractWindow):
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar. The statusbar can be populated by messages
    with different levels of sevirity, from 0 (debug) to 9 (error).
    Stuff like that should be defined in a AbstractWindow class.
    """

    def __init__(self):
	win = gtk.Window ()
	accelgroup = gtk.AccelGroup()
	statusbar = gtk.Statusbar()
	model = namespace.NamespaceModel(UML.ElementFactory())
	view = namespace.NamespaceView(model)
	menubar = gtk.MenuBar()

	vbox = gtk.VBox(homogeneous=gtk.FALSE)
	win.add (vbox)
	win.add_accel_group (accelgroup)
	
	vbox.pack_start(menubar, gtk.FALSE, gtk.FALSE, 0)
	vbox.pack_start(view)
	vbox.pack_end(statusbar, gtk.FALSE, gtk.FALSE, 0)

	self.__win = win
	self.__accelgroup = accelgroup
	self.__statusbar = statusbar
	self.__model = model
	self.__view = view
	self.__menubar = menubar

	win.show_all()
	
	self.statusbar.push (0, 'Welcome...')

    def push(self, message):
	self.statusbar.push (0, message)
	# TODO: create timeout

    def __execute_command(self, menu_item, command):
	try:
	    command.execute()
	except Exception, e:
	    self.push('Operation failed: ' + e)

