# vim: sw=4

import types

__version__ = "$Revision$"
__author__ = "Arjan Molenaar"
__date__ = "2002-08-28"

class Signal:
    """
    The signal class is an implementation of the Observer pattern. It can be
    used to send signals to every function or method that connected to the
    signal object, with a variable amount of parameters. Note that the owner
    of the Signal instance should define a protocol for notifying the observers.
    The subject should provide methods for connecting and disconnecting
    observers (preferably 'connect()' and 'disconnect()'.
    """
    def __init__(self):
	# Signals are stored in a list as [ (signal_func, (data)), <next sig> ]
        self.__signals = [ ]

    def connect (self, signal_handler, *data):
	"""
	Connect to the object. You should provide a signal handler and a
	bunch of parameters that should be passed to the signal handler.
	"""
	#print 'Signal.connect():', data
	self.__signals.append ((signal_handler,) + data)

    def disconnect (self, signal_handler):
        """
	Disconnect the signal_handler (observer).
	"""
	self.__signals = filter (lambda o: o[0] != signal_handler,
				 self.__signals)

    def emit (self, *keys):
        """
	Emit the signal. A set of parameters can be defined that will be
	passed to the signal handler. Those parameters will be set before
	the parameters provided through the connect() method.

	Note that you should define how many parameters are provided by the
	owner of the signal.
	"""
	#print 'Signal.emit():', self.__signals
        for signal in self.__signals:
	    signal_handler = signal[0]
	    data = keys + signal[1:]
	    #print 'signal:', signal_handler, data
	    signal_handler (*data)

