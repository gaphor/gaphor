
# vim:sw=4

import gtk
import bonobo.ui
import gnome.ui
import namespace
import command.file
import command.diagram
import command.about
import gaphor.UML as UML
import gaphor.config
#from gaphor.misc.menufactory import MenuFactory, Menu, MenuItem, MenuSeparator, MenuPlaceholder, MenuStockItem
import stock
from abstractwindow import AbstractWindow

class MainWindow(AbstractWindow):
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar.
    """

    def __init__(self):
	pass

    def get_title(self):
	return 'Gaphor v0.1.0'

    def get_name(self):
	return 'gaphor.main'

    def create_contents(self):
	model = namespace.NamespaceModel(GaphorResource(UML.ElementFactory))
	view = namespace.NamespaceView(model)
	self.__model = model
	self.__view = view

	return view

    def get_ui_xml_file(self):
	return 'gaphor-ui.xml'

    def get_default_size(self):
	return (200, 300)

