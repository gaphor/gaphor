#!/usr/bin/env python
# vim:sw=4
"""This is Gaphor, a Python based UML editor.
"""

__all__ = [ 'main', 'resource', 'GaphorError' ]

# Check for GTK-2.0, since we need it anyway...
import pygtk
pygtk.require('2.0')
del pygtk

import misc.singleton
import misc.logger
import version
import types

import gaphor.version

_resources = {
    'Name': 'gaphor',
    'Version': gaphor.version.VERSION,
    'DataDir': gaphor.version.DATA_DIR
}

_main_window = None

class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
            self.args = args


def main():
    """Start the interactive application.
    """
    global _resources
    # Import stuff here, since the user might not need all the GUI stuff
    import gtk
    #import bonobo
    #import gnome
    # Initialize gnome.ui, since we need some definitions from it
    #import gnome.ui
    from ui import MainWindow
    #gnome.init('gaphor', gaphor.version.VERSION)
    # should we set a default icon here or something?
    main_window = MainWindow()
    main_window.construct()
    # When the state changes to CLOSED, quit the application
    #main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and bonobo.main_quit())
    main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and gtk.main_quit())
    #mainwin = GaphorResource(WindowFactory).create(type=MainWindow)
    _resources['MainWindow'] = main_window
    #gtk.threads_init()
    #gtk.threads_enter()
    gtk.main()
    #gtk.threads_leave()
    log.info('Bye!')


def get_conf(self, key):
    if not self.__conf:
	from gaphor.misc.conf import Conf
	self.__conf = Conf(self.NAME)
    return self.__conf[key]


_no_default = []

def resource(r, default=_no_default):
    """Locate a resource.

    Resource should be the class of the resource to look for or a string. In
    case of a string the resource will be looked up in the GConf configuration.

    example: Get the element factory:
	    factory = gaphor.resource(gaphor.UML.ElementFactory)

    Also builtin resources are 'Name', 'Version' and 'DataDir'. In case main()
    is run, 'MainWindow' points to the main window of the application.

    If a class name is given as a resource, the resource is created if not
    yet available. If the resource is a string, KeyError is issued if the
    resource could not be localed, unless a default value was set.
    """
    global _resources
    try:
	return _resources[r]
    except KeyError:
	pass
    # Handle string-like resources 
    if isinstance (r, types.StringType):
	# TODO: It might be a GConf resource string

	if default is not _no_default:
	    return default
	raise KeyError, 'No resource with name "%s"' % r
    # Instantiate the resource and return it
    i = r()
    _resources[r] = i
    _resources[r.__name__] = i
    return i


import __builtin__
__builtin__.__dict__['log'] = misc.logger.Logger()

if __debug__: 
    refs = []

