# vim:sw=4

from gaphor.misc.signal import Signal

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
	self.__state = AbstractWindow.STATE_INIT
	self.__signal = Signal()

    def get_window(self):
    	raise NotImplementedError, 'get_window() should return the gtk.Window or bonobo.ui.Window associated with this window.'

    def set_owner(self, owner):
	raise NotImplementedError, 'set_owner() should assign the window as a child window of owner.'

    def get_state(self):
	return self.__state

    def construct(self):
	raise NotImplementedError, 'construct() should create GUI components.'

    def close(self):
	raise NotImplementedError, 'close() should destroy the GUI components.'

    def connect(self, signal_func, *data):
	"""
	Connect to the window. A signal is emited when the state changes.
	"""
	self.__signal.connect(signal_func, *data)

    def disconnect(self, signal_func):
	self.__signal.disconnect(signal_func)


    # Protected:

    def _set_state(self, state):
	"""
	Protected method. Should be called to change the state.
	"""
	if state > self.__state:
	    self.__state = state
	    self.__signal.emit()

    def _check_state(self, state):
	assert self.__state == state, 'Method was called with an invalid state. State is %d' % self.__state
