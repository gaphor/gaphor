# vim:sw=4:et

import gobject, gtk
import gaphor
from gaphor.misc.signal import Signal
from gaphor.misc.logger import Logger
#from commandregistry import CommandRegistry
from gaphor.misc.action import Action, ActionPool, register_action
from menufactory import MenuFactory

class CloseAction(Action):
    id = 'WindowClose'

    def init(self, window):
        pass

register_action(CloseAction)

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

    menu = ()
    toolbar = ()

    def __init__(self):
        self.__state = AbstractWindow.STATE_INIT
        self.__signal = Signal()

        self.name = None
        self.window = None
        self.statusbar = None
        self.accel_group = None
        self.action_pool = ActionPool(self._action_initializer)
        self.menu_factory = None

        # The page can also be constructed as a notebook page
        self.sub_window = True
        self.notebook_page_number = -1

    def get_window(self):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        return self.window

    def get_action_pool(self):
        return self.action_pool

    def get_state(self):
        return self.__state

    def set_owning_window(self, window):
        self.owning_window = window

    def construct(self):
        raise NotImplementedError, 'construct() should create GUI components.'

    def execute_action(self, action_id):
        self.action_pool.execute(action_id)

    def set_message(self, message):
        """Set a message in the window's status bar."""
        self._check_state(AbstractWindow.STATE_ACTIVE)
        #self.__ui_component.set_status(message or ' ')

    def close(self):
        """Close the window."""
        self._check_state(AbstractWindow.STATE_ACTIVE)
        if self.sub_window:
            self.window.destroy()
        else:
            self.owning_window.remove_tab(self)
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

#    def _set_log_message(self, level, message, exc=None):
#        """Set log messages with level INFO or higher in the status bar."""
#        if level > Logger.DEBUG:
#            self.set_message(str(message))
#            main = gobject.main_context_default()
#            # If an exception is provided, also send the message to stdout
#            if exc:
#                log.default_logger(level, message, exc)
#            while main.pending():
#                    main.iteration(False)
#            #return True

    def _action_initializer(self, action):
        try:
            action.init(self)
        except Exception, e:
            log.warning(str(e), e)


    def _construct_window(self, name, title, size, contents):
        """Construct a Window.
        
        Name is the window's name. Title is the title of the window. Size
        is a tuple (x, y) which gives a requested size for the window.
        Contents is a widget that holds the contents of the window. Params
        is a dictionary of parameter:value pairs which are passed to the
        commands after creation.
        """
        self._check_state(AbstractWindow.STATE_INIT)

        self.name = name

        self._set_state(AbstractWindow.STATE_ACTIVE)

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title(title)

        window.set_size_request(size[0], size[1])
        window.set_resizable(True)

        vbox = gtk.VBox()
        window.add(vbox)
        vbox.show()

        accel_group = gtk.AccelGroup()
        window.add_accel_group(accel_group)
        #window.set_accel_path('/', accel_group)

        statusbar = gtk.Statusbar()
        vbox.pack_end(statusbar, expand=False)
        statusbar.show()

        # Set the contents:
        vbox.pack_end(contents, expand=True)

        self.menu_factory = MenuFactory(self.action_pool,
                                        accel_group=accel_group,
                                        statusbar=statusbar,
                                        statusbar_context=0)

        menubar = self.menu_factory.create_menu(self.menu)
        vbox.pack_start(menubar, expand=False)
        menubar.show()

        if self.toolbar:
            toolbar = self.menu_factory.create_toolbar(self.toolbar)
            #handle_box = gtk.HandleBox()
            #handle_box.add(toolbar)
            vbox.pack_start(toolbar, expand=False)
            #vbox.pack_start(handle_box, expand=False)
            #handle_box.show()
            toolbar.show()

        self.__destroy_id = window.connect('destroy', self._on_window_destroy)
        # On focus in/out a log handler is added to the logger.
        #window.connect('focus_in_event', self._on_window_focus_in_event)
        #window.connect('focus_out_event', self._on_window_focus_out_event)
        # Set state before commands are created, so the commands can use
        # the get_* methods.

        window.show()

        self.window = window
        self.statusbar = statusbar
        self.accel_group = accel_group


    def _construct_popup_menu(self, menu_def, event):
        """Create a popup menu.
        
        Popup is the name of the popup menu in the Bonobo UI xml file.
        Elements is a list of objects for which menu items should be created
        (as defined in the 'subject' attribute of CommandInfo).
        Event is the event that causes the popup menu (such as a button press)
        Params is a dictionary of parameter:value pairs which are passed to the
        commands after creation.
        If some items in the elements list contain the has_capability() method,
        capabilities of these items are compared to capabilities required
        for an item to be sensitive/have a state.
        """
        self._check_state(AbstractWindow.STATE_ACTIVE)

        menu = self.menu_factory.create_popup(menu_def, fire_and_forget=True)
        menu.popup(None, None, None, event.button, event.time)

    def _on_window_destroy(self, window):
        """Window is destroyed. Do the same thing that would be done if
        File->Close was pressed.
        """
        self._check_state(AbstractWindow.STATE_ACTIVE)
        #log.remove_logger(self._set_log_message)
        self._set_state(AbstractWindow.STATE_CLOSED)
        del self.window
        #del self.__ui_component

