
# vim:sw=4

import gtk
import bonobo
import bonobo.ui
import namespace
import gaphor.UML as UML
import gaphor.config as config
from menufactory import MenuFactory

class MainWindow(object):
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar.
    """

    def __init__(self):
	pass

    def get_window(self):
	return self.__window

    def get_model(self):
	return self.__model

    def get_view(self):
	return self.__view

    def get_ui_component(self):
	return self.__ui_component

    def construct(self):
	window = bonobo.ui.Window ('gaphor', 'Gaphor v' + config.VERSION)
	window.set_size_request(200, 300)
	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	ui_engine = window.get_ui_engine ()
	ui_engine.config_set_path (config.CONFIG_PATH)
	ui_component = bonobo.ui.Component ('gaphor')
	ui_component.set_container (ui_container.corba_objref ())

	bonobo.ui.util_set_ui (ui_component, config.DATADIR,
			       'gaphor-ui.xml', config.PACKAGE_NAME)
	
	model = namespace.NamespaceModel(GaphorResource(UML.ElementFactory))
	view = namespace.NamespaceView(model)

	window.set_contents(view)
	
	window.show_all()

	window.connect ('destroy', self.__destroy_event_cb)

	self.__window = window
	self.__ui_component = ui_component
	self.__model = model
	self.__view = view

	# Set commands:
	command_registry = GaphorResource('CommandRegistry')
	ui_component.set_translate ('/', command_registry.create_command_xml(context='main.menu'))
	verbs = command_registry.create_verbs(context='main.menu',
					      params={ 'window': self })
	ui_component.add_verb_list (verbs, None)

    def __destroy_event_cb (self, window):
	bonobo.main_quit()
