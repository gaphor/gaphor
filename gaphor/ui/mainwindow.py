
# vim:sw=4

import gtk
import bonobo
import bonobo.ui
import namespace
import gaphor.UML as UML
import gaphor.config as config
from abstractwindow import AbstractWindow

class MainWindow(AbstractWindow):
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar.
    """

    def __init__(self):
	AbstractWindow.__init__(self)
	self.__transient_window = list()

    def get_window(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__window

    def get_model(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__model

    def get_view(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__view

    def get_ui_component(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__ui_component

    def construct(self):
	self._check_state(AbstractWindow.STATE_INIT)
	window = bonobo.ui.Window ('gaphor', 'Gaphor v' + config.VERSION)
	window.set_size_request(200, 300)
	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	ui_engine = window.get_ui_engine ()
	ui_engine.config_set_path (config.CONFIG_PATH)
	ui_component = bonobo.ui.Component ('tree')
	ui_component.set_container (ui_container.corba_objref ())

	bonobo.ui.util_set_ui (ui_component, config.DATADIR,
			       'gaphor-ui.xml', config.PACKAGE_NAME)
	
	model = namespace.NamespaceModel(GaphorResource(UML.ElementFactory))
	view = namespace.NamespaceView(model)

	window.set_contents(view)
	
	window.show_all()

	self.__destroy_id = window.connect ('destroy', self.__on_window_destroy)
	view.connect_after ('event', self.__on_view_event)
	view.connect ('row_activated', self.__on_view_row_activated)

	self.__window = window
	self.__ui_component = ui_component
	self.__model = model
	self.__view = view

	self._set_state(AbstractWindow.STATE_ACTIVE)

	# Set commands:
	command_registry = GaphorResource('CommandRegistry')
	ui_component.set_translate ('/', command_registry.create_command_xml(context='main.'))
	verbs = command_registry.create_verbs(context='main.menu',
					      params={ 'window': self })
	ui_component.add_verb_list (verbs, None)

    def set_message(self, message):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__ui_component.set_status(message)

    def add_transient_window(self, window):
	"""
	Add a window as a sub-window of the main application.
	"""
	mywin = self.__window
	window_win = window.get_window()
	window_win.add_accel_group(mywin.get_accel_group())
	window_win.set_transient_for (mywin)
	self.__transient_window.append(window)
	window.connect(self.__on_transient_window_closed)

    def close(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__window.destroy()
	self._check_state(AbstractWindow.STATE_CLOSED)

    def __on_window_destroy (self, window):
	"""
	Window is destroyed... Quit the application.
	"""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	log.debug ('Destroying main window...')
	self._set_state(AbstractWindow.STATE_CLOSED)
	del self.__window
	del self.__ui_component
	del self.__model
	del self.__view

    def __on_view_row_activated(self, view, path, column):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	item = self.get_model().on_get_iter(path)
	cmd_reg = GaphorResource('CommandRegistry')
	cmd = cmd_reg.create_command('OpenModelElement')
	cmd.set_parameters({ 'window': self,
			     'element': item })
	cmd.execute()

    def __on_view_event(self, view, event):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	# handle mouse button 3:
	if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
		selection = view.get_selection()
		model, iter = selection.get_selected()
		if not iter:
		    return
		element = model.get_value(iter, 0)
		cmd_reg = GaphorResource('CommandRegistry')
		verbs = cmd_reg.create_verbs(context='main.popup',
					     params={ 'window': self,
						      'element': element })
		self.__ui_component.add_verb_list (verbs, None)
		menu = gtk.Menu()
		# The window takes care of destroying the old menu, if any...
		self.__window.add_popup(menu, '/popups/NamespaceView')
		menu.popup(None, None, None, event.button, 0)

    def __on_transient_window_closed(self, window):
	assert window in self.__transient_window
	log.debug('%s closed.' % window)
	self.__transient_window.remove(window)

    def __on_transient_window_notify_title(self, window):
	pass

