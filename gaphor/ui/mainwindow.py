
# vim:sw=4

import gtk
import gnome.ui
import namespace
import command.file
import gaphor.UML as UML
import gaphor.config
from gaphor.misc.menufactory import MenuFactory, MenuItem, MenuSeparator

class MainWindow:
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar.
    """

    def __2init__(self):
	# Menu items have the following structure:
	# ( Name, Comment, (ctrl) + Modifier, Command or Submenu )
	menu =  MenuItem(submenu=(
		    MenuItem(name='_File', submenu=(
			MenuItem(stock=gtk.STOCK_NEW,
				 comment='Create a new model',
				 command=command.file.NewCommand()),
	 		MenuItem(stock=gtk.STOCK_OPEN,
				 comment='Open an existing model',
				 command=command.file.OpenCommand()),
			MenuItem(stock=gtk.STOCK_SAVE,
				 comment='Save current model',
				 command=command.file.SaveCommand()),
			MenuSeparator(),
			MenuItem(stock=gtk.STOCK_QUIT,
				 comment='Exit Gaphor',
				 command=command.file.QuitCommand())
			,))
		    ,))
	win = gtk.Window ()
	accelgroup = gtk.AccelGroup()
	statusbar = gtk.Statusbar()
	model = namespace.NamespaceModel(UML.ElementFactory())
	view = namespace.NamespaceView(model)

	menu_factory = MenuFactory(menu=menu, accelgroup=accelgroup, statusbar=statusbar)
	menubar = menu_factory.create_menu()

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
	
	statusbar.push (0, 'Gaphor v%s' % gaphor.config.GAPHOR_VERSION)

    def __init__(self, name, title):
	# Menu items have the following structure:
	# ( Name, Comment, (ctrl) + Modifier, Command or Submenu )
	menu =  MenuItem(submenu=(
		    MenuItem(name='_File', submenu=(
			MenuItem(stock=gtk.STOCK_NEW,
				 comment='Create a new model',
				 command=command.file.NewCommand()),
	 		MenuItem(stock=gtk.STOCK_OPEN,
				 comment='Open an existing model',
				 command=command.file.OpenCommand()),
			MenuItem(stock=gtk.STOCK_SAVE,
				 comment='Save current model',
				 command=command.file.SaveCommand()),
			MenuSeparator(),
			MenuItem(stock=gtk.STOCK_QUIT,
				 comment='Exit Gaphor',
				 command=command.file.QuitCommand())
			,))
		    ,))
	app = gnome.ui.App (name, title)
	app.set_default_size (200, 300)
	accelgroup = gtk.AccelGroup()
	app.add_accel_group (accelgroup)
	app_bar = gnome.ui.AppBar (has_progress=0, has_status=1,
				   interactivity=gnome.ui.PREFERENCES_USER)
	app.set_statusbar(app_bar)
	model = namespace.NamespaceModel(UML.ElementFactory())
	view = namespace.NamespaceView(model)

	menu_factory = MenuFactory(menu=menu, accelgroup=accelgroup,
				   statusbar=app_bar)
	menubar = menu_factory.create_menu()

	app.set_menus(menubar)
	app.set_contents(view)

	self.__app = app
	self.__model = model
	self.__view = view
	self.__menubar = menubar
	self.__windows = []
	app.show_all()
	
    def add_window(self, window):
	self.__windows.append(window)

