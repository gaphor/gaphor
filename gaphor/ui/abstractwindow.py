# vim:sw=4

from gaphor.misc.signal import Signal
from gaphor.misc.logger import Logger
from commandregistry import CommandRegistry
import gobject, gtk, bonobo.ui
from gaphor import Gaphor

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
	self.__popups = dict()
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
	"""Set a capabiliti active or inactive. This will cause menu items
	to become (in)sensitive."""
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
	"""Disconnect a previously connected signal handler."""
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

    def _set_log_message(self, level, message, exc=None):
	"""Set log messages with level INFO or higher in the status bar."""
	if level > Logger.DEBUG:
	    self.set_message(message)
	    main = gobject.main_context_default()
	    # If an exception is provided, also send the message to stdout
	    if exc:
		log.default_logger(level, message, exc)
	    while main.pending():
	    	main.iteration(False)
	    return True

    def _construct_window(self, name, title, size, contents, params):
	"""Construct a BonoboWindow.
	
	Name is the window's name. Title is the title of the window. Size
	is a tuple (x, y) which gives a requested size for the window.
	Contents is a widget that holds the contents of the window. Params
	is a dictionary of parameter:value pairs which are passed to the
	commands after creation."""
	self._check_state(AbstractWindow.STATE_INIT)
	self.__name = name
	window = bonobo.ui.Window ('gaphor.' + name, title)

	window.set_size_request(size[0], size[1])
	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	ui_engine = window.get_ui_engine ()
	ui_engine.config_set_path ('/apps/gaphor/UIConfig/kvps/bonoboengine')
	ui_component = bonobo.ui.Component (name)
	ui_component.set_container (ui_container.corba_objref ())

	gaphor = Gaphor()
	bonobo.ui.util_set_ui (ui_component, gaphor.get_datadir(),
			       'gaphor-' + name + '-ui.xml',
			       gaphor.NAME)
	window.set_contents(contents)
	self.__destroy_id = window.connect('destroy', self._on_window_destroy)
	# On focus in/out a log handler is added to the logger.
	window.connect('focus_in_event', self._on_window_focus_in_event)
	window.connect('focus_out_event', self._on_window_focus_out_event)
	# Set state before commands are created, so the commands can use
	# the get_* methods.
	self._set_state(AbstractWindow.STATE_ACTIVE)

	# Set commands, for menu and (possible) popup menus:
	command_registry = GaphorResource(CommandRegistry)

	ui_component.set_translate ('/', command_registry.get_command_xml(context=name + '.'))
	verbs = command_registry.get_verbs(context=name + '.menu',
					   params=params)
	ui_component.add_verb_list (verbs, None)

	listeners = command_registry.get_listeners(context=name + '.menu',
						   params=params)
	for n, c in listeners:
	    ui_component.add_listener(n, c)

	window.show_all()

	self.__window = window
	self.__ui_component = ui_component

    def _construct_popup_menu(self, popup, elements, event, params):
	"""Create a popup menu.
	
	Popup is the name of the popup menu in the Bonobo UI xml file.
	Elements is a list of objects for which menu items should be created
	(as defined in the 'subject' attribute of CommandInfo).
	Event is the event that causes the popup menu (such as a button press)
	Params is a dictionary of parameter:value pairs which are passed to the
	commands after creation.
	If some items in the elements list contain the has_capability() method,
	capabilities of these items are compared to capabilities required
	for an item to be sensitive/have a state."""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	context = self.__name + '.popup'
	capable_elements = list()
	command_registry = GaphorResource(CommandRegistry)

	# Create commands with the right parameters set:
	ui_component = self.__ui_component
	verbs = command_registry.get_verbs(context, params)
	ui_component.add_verb_list (verbs, None)

	# Listeners should be added for toggle and radio buttons:
	# First move existing listeners, fo commands are not executed
	# by accident.
	listeners = command_registry.get_listeners(context, params)
	for n, c in listeners:
	    ui_component.remove_listener(n)

	for name, klass in command_registry.get_subjects(context):
	    hidden = '1'
	    for e in elements:
		if isinstance(e, klass):
		    hidden = '0'
		    if hasattr(e, 'has_capability'):
			#log.debug('%s.has_capability found.' % e)
			capable_elements.append(e)
		    break
	    if not name.startswith('/'):
		name = '/commands/' + name
	    ui_component.set_prop(name, 'hidden', hidden)

	# Creating a brand new menu every time does something wierd with
	# callbacks.
	if self.__popups.has_key(popup):
	    menu = self.__popups[popup]
	else:
	    menu = gtk.Menu()
	    self.__window.add_popup(menu, '/popups/' + popup)
	    self.__popups[popup] = menu

	# Set items possible visible:
	if capable_elements:
	    for name, type, caps in command_registry.get_capabilities(context):
		#log.debug('Checking caps for %s %s' % (name, caps))
		for e in capable_elements:
		    is_disabled = False
		    for c in caps:
			if not e.has_capability(c):
			    # disable the command:
			    log.debug('disabling command %s' % name)
			    ui_component.set_prop('/commands/' + name,
						  type, '0')
			    is_disabled = True
			    break
		    else:
			# all capabilities are available:
			log.debug('enabling command %s' % name)
			ui_component.set_prop('/commands/' + name,
					      type, '1')
		    if is_disabled:
			break
	
	# Add listeners again, now we can serve the user:
	for n, c in listeners:
	    ui_component.add_listener(n, c)

	menu.popup(None, None, None, event.button, 0)

    def _on_window_focus_in_event(self, window, event):
	log.add_logger(self._set_log_message)

    def _on_window_focus_out_event(self, window, event):
	log.remove_logger(self._set_log_message)

    def _on_window_destroy(self, window):
	"""Window is destroyed. Do the same thing that would be done if
	File->Close was pressed."""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	log.remove_logger(self._set_log_message)
	self._set_state(AbstractWindow.STATE_CLOSED)
	del self.__window
	del self.__ui_component

    def _on_capability_update(self):
	"""Activate or deactivate commands with capabilities."""
	if self.__state == AbstractWindow.STATE_ACTIVE:
	    command_registry = GaphorResource(CommandRegistry)
	    _caps = self.__capabilities
	    for name, type, caps in command_registry.get_capabilities(self.__name + '.menu'):
		#log.debug('Checking caps for %s %s' % (name, caps))
		for c in caps:
		    if c not in _caps:
			# disable the command:
			self.__ui_component.set_prop('/commands/' + name,
						     type, '0')
			break
		else:
		    # all capabilities are available:
		    self.__ui_component.set_prop('/commands/' + name,
						 type, '1')
	# Returning False will cause the method not to be called again
	self.__update_id = 0
	return False

