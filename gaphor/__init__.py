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
import types

import version

from misc.resource import Resource

# Application wide resources can be stored in the 'resource' like this
#
# >>> resource('myResource', some_value)
#
# If the resource doesn't already exist, it is created, otherwise the existing
# resource is returned.
resource = Resource(initial_resources = {
			'Name': 'gaphor',
			'Version': version.VERSION,
			'DataDir': version.DATA_DIR,
			'UserDataDir': version.USER_DATA_DIR
		    })

class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
	    Exception.__init__(self)
            self.args = args

def main():
    """Start the interactive application.
    """
    # Import stuff here, since the user might not need all the GUI stuff
    import gtk
    # Load plugin definitions:
    import diagram
    import pluginmanager
    from ui.mainwindow import MainWindow

    resource('PluginManager').bootstrap()

    # should we set a default icon here or something?
    main_window = resource(MainWindow)
    main_window.construct()
    # When the state changes to CLOSED, quit the application
    main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and gtk.main_quit())
    # Make the mainwindow accessable as a resource
    #gtk.threads_init()
    #gtk.threads_enter()
    # Start with a clean nice new model
    main_window.execute_action('FileNew')
    gtk.main()
    #gtk.threads_leave()
    log.info('Bye!')

# TODO: Remove this
import __builtin__
__builtin__.__dict__['log'] = misc.logger.Logger()

if __debug__: 
    refs = []

