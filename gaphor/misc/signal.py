# vim: sw=4

import types

__version__ = "$Revision$"
__author__ = "Arjan Molenaar"
__date__ = "2002-03-19"

class Signal:
    """
    The signal class can be used to send signals to whatever function or
    method connected to the signal object. Signals are handy for notifying
    a large amount of objects that a property has changed.
    Those signal objects are owned by some other object. That object should
    provide an interface for connecting and disconnecting signal handlers
    as well as define how many parameters are provided by the owner provides
    when the signal is emited.
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
	Disconnect all calls to the signal_handler.
	"""
	self.__signals = filter (lambda o: o[0] != signal_handler,
				 self.__signals)

    def emit (self, *keys):
        """
	Emit the signal. a set of parameters can be defined that will be
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

