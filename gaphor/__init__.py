#!/usr/bin/env python
# vim:sw=4
"""This is Gaphor, a Python based UML editor.
"""

__all__ = [ 'main', 'resource', 'GaphorError' ]

# Check for GTK-2.0, since we need it anyway...
#import pygtk
#pygtk.require('2.0')
#del pygtk

import misc.logger

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
                        'UserDataDir': version.USER_DATA_DIR,
                        'ui.toolbox.classes': True,
                    })

class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
            Exception.__init__(self)
            self.args = args

def main(gaphor_file=None):
    """Start the interactive application.

    This involves importing plugins and creating the main window.
    """
    # Import GUI stuff here, since the user might not need all the GUI stuff
    import gtk
    import ui
    import adapters
    import actions
    # Load plugin definitions:
    import pluginmanager
    from ui.mainwindow import MainWindow

    resource('PluginManager').bootstrap()

    ui.load_accel_map()

    # should we set a default icon here or something?
    main_window = resource(MainWindow)
    main_window.construct()
    # When the state changes to CLOSED, quit the application
    main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and gtk.main_quit())

    #gtk.threads_init()
    #gtk.threads_enter()
    if gaphor_file:
        main_window.set_filename(gaphor_file)
        main_window.execute_action('FileRevert')
    else:
        main_window.execute_action('FileNew')

    gtk.main()
    #gtk.threads_leave()

    resource.save()

    ui.save_accel_map()

    log.info('Bye!')


# TODO: Remove this
import __builtin__
__builtin__.__dict__['log'] = misc.logger.Logger()

if __debug__: 
    refs = []

