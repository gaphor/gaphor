# vim:sw=4

from gaphor.misc.signal import Signal
from commandregistry import CommandRegistry
import bonobo.ui
import gaphor.config as config
import gobject

class AbstractWindow(object):
    """
    AbstractWindow is an abstract base class for window shell related classes.
    The actual windows are created by the WindowFactory. The methods defined
    here should be overriden in window shell implementations.

    An AbstractWindow behaves as a little state machine. Three states can be
    passed:
    STATE_INIT: The initial state
    STATE_ACTIVE: The GUI components are created and shown 
    STATE_CLOSE: The window is closed and no interaction can be done with the
    		 window anymore.
    """
    STATE_INIT=1
    STATE_ACTIVE=2
    STATE_CLOSED=3

    def __init__(self):
	self.__name = None
	self.__state = AbstractWindow.STATE_INIT
	self.__signal = Signal()
	self.__capabilities = list()
	self.__update_id = gobject.idle_add(self._on_capability_update)

    def get_window(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__window

    def get_ui_component(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__ui_component

    def get_state(self):
	return self.__state

    def construct(self):
	raise NotImplementedError, 'construct() should create GUI components.'

    def set_message(self, message):
	"""Set a message in the window's status bar."""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__ui_component.set_status(message or ' ')

    def set_capability(self, capability, active):
	if active and capability not in self.__capabilities:
	    #log.debug('set capability %s' % capability)
	    self.__capabilities.append(capability)
	    if self.__update_id == 0:
		self.__update_id = gobject.idle_add(self._on_capability_update)
	elif not active and capability in self.__capabilities:
	    #log.debug('unset capability %s' % capability)
	    self.__capabilities.remove(capability)
	    if self.__update_id == 0:
		self.__update_id = gobject.idle_add(self._on_capability_update)

    def close(self):
	"""Close the window."""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__window.destroy()
	self._set_state(AbstractWindow.STATE_CLOSED)

    def connect(self, signal_func, *data):
	"""Connect to the window. A signal is emited when the state changes."""
	self.__signal.connect(signal_func, *data)

    def disconnect(self, signal_func):
	self.__signal.disconnect(signal_func)


    # Protected:

    def _set_state(self, state):
	"""Protected method. Should be called to change the state."""
	if state > self.__state:
	    self.__state = state
	    self.__signal.emit(self)

    def _check_state(self, state):
	"""Raise an assert error if the state is not @state."""
	assert self.__state == state, 'Method was called with an invalid state. State is %d' % self.__state
	return True

    def _construct_window(self, name, title, size, contents, params):
	"""Construct a BonoboWindow."""
	self._check_state(AbstractWindow.STATE_INIT)
	self.__name = name
	window = bonobo.ui.Window ('gaphor.' + name, title)

	window.set_size_request(size[0], size[1])
	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	ui_engine = window.get_ui_engine ()
	ui_engine.config_set_path (config.CONFIG_PATH + '/bonoboengine')
	ui_component = bonobo.ui.Component (name)
	ui_component.set_container (ui_container.corba_objref ())

	bonobo.ui.util_set_ui (ui_component, config.DATADIR,
			       'gaphor-' + name + '-ui.xml',
			       config.PACKAGE_NAME)
	window.set_contents(contents)

	self.__destroy_id = window.connect('destroy', self._on_window_destroy)
	# Set state before commands are created, so the commands can use
	# the get_* methods.
	self._set_state(AbstractWindow.STATE_ACTIVE)

	# Set commands:
	command_registry = GaphorResource(CommandRegistry)

	ui_component.set_translate ('/', command_registry.get_command_xml(context=name + '.'))
	verbs = command_registry.get_verbs(context=name + '.menu', params=params)
	ui_component.add_verb_list (verbs, None)

	window.show_all()

	self.__window = window
	self.__ui_component = ui_component

    def _construct_popup_menu(self, name, event, params):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	command_registry = GaphorResource(CommandRegistry)
	verbs = command_registry.get_verbs(name=self.__name + '.popup',
					   params=params)
	self.__ui_component.add_verb_list (verbs, None)
	menu = gtk.Menu()
	# The window takes care of destroying the old menu, if any...
	self.__window.add_popup(menu, '/popups/' + name)
	menu.popup(None, None, None, event.button, 0)

    def _on_window_destroy(self, window):
	"""
	Window is destroyed. Do the same thing that would be done if
	File->Close was pressed.
	"""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self._set_state(AbstractWindow.STATE_CLOSED)
	del self.__window
	del self.__ui_component

    def _on_capability_update(self):
	"""Activate or deactivate commands with capabilities."""
	if self.__state == AbstractWindow.STATE_ACTIVE:
	    com_reg = GaphorResource(CommandRegistry)
	    self_caps = self.__capabilities
	    log.debug('Capabilities are %s' % self_caps)
	    for name, type, caps in com_reg.get_capabilities(self.__name + '.'):
		log.debug('Checking caps for %s %s' % (name, caps))
		for c in caps:
		    if c not in self_caps:
			# disable the command:
			#log.debug('disable command %s (%s)' % (name, type))
			self.__ui_component.set_prop('/commands/' + name,
						     type, '0')
			break
		else:
		    # all capabilities are available:
		    #log.debug('enable command %s (%s)' % (name, type))
		    self.__ui_component.set_prop('/commands/' + name,
						 type, '1')
	# Returning False will cause the method not to be called again
	self.__update_id = 0
	return False

