
# vim:sw=4

import gtk
import namespace
import gaphor
import gaphor.UML as UML
from abstractwindow import AbstractWindow

class MainWindow(AbstractWindow):
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar.
    """

    def __init__(self):
	AbstractWindow.__init__(self)
	self.__filename = None
	self.__transient_windows = list()
	# Act on changes in the element factory resource
	factory = gaphor.resource(UML.ElementFactory)
	factory.connect(self.__on_element_factory_signal)

    def get_model(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__model

    def get_view(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__view

    def set_filename(self, filename):
	self.__filename = filename

    def get_filename(self):
	return self.__filename

    def get_transient_windows(self):
	return self.__transient_windows

    def construct(self):
	model = namespace.NamespaceModel(gaphor.resource(UML.ElementFactory))
	view = namespace.NamespaceView(model)
	scrolled_window = gtk.ScrolledWindow()
	scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
	scrolled_window.add(view)
	
	view.connect_after ('event-after', self.__on_view_event)
	view.connect ('row_activated', self.__on_view_row_activated)

	self.__model = model
	self.__view = view


	self._construct_window(name='main',
			       title='Gaphor v' + gaphor.resource('Version'),
			       size=(220, 400),
			       contents=scrolled_window,
			       params={ 'window': self })

    def add_transient_window(self, window):
	"""
	Add a window as a sub-window of the main application.
	"""
	mywin = self.get_window()
	window_win = window.get_window()
	window_win.add_accel_group(mywin.get_accel_group())
	#window_win.set_transient_for (mywin)
	self.__transient_windows.append(window)
	window.connect(self.__on_transient_window_closed)

    def _on_window_destroy (self, window):
	"""
	Window is destroyed... Quit the application.
	"""
	AbstractWindow._on_window_destroy(self, window)
	gaphor.resource(UML.ElementFactory).disconnect(self.__on_element_factory_signal)
	del self.__model
	del self.__view

    def __on_view_row_activated(self, view, path, column):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	node = self.get_model().node_from_path(path)
	element = self.get_model().element_from_node(node)
	cmd_reg = gaphor.resource('CommandRegistry')
	cmd = cmd_reg.get_command('main.popup', 'OpenModelElement')
	cmd.set_parameters({ 'window': self,
			     'element': element })
	cmd.execute()

    def __on_view_event(self, view, event):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	# handle mouse button 3:
	if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
	    selection = view.get_selection()
	    model, iter = selection.get_selected()
	    assert model is self.__model
	    if not iter:
		return
	    element = model.get_value(iter, 0)
	    path = model.path_from_element(element)
	    self._construct_popup_menu(popup='NamespaceView',
				       elements=[element],
				       event=event,
				       params={ 'window': self,
					        'element': element,
					        'iterator': iter,
					        'path': path })

    def __on_transient_window_closed(self, window):
	assert window in self.__transient_windows
	log.debug('%s closed.' % window)
	self.__transient_windows.remove(window)

    def __on_transient_window_notify_title(self, window):
	pass

    def __on_element_factory_signal(self, obj, key):
	#print '__on_element_factory_signal', key
	factory = gaphor.resource(UML.ElementFactory)
	self.set_capability('model', not factory.is_empty())

