#!/usr/bin/env python
# vim:sw=4
"""This is Gaphor, a Python based UML editor.
"""

__all__ = [ 'main', 'resource', 'GaphorError' ]

import os

import misc.logger

from misc.resource import Resource

if os.name == 'nt':
    home = 'USERPROFILE'
else:
    home = 'HOME'

user_data_dir = os.path.join(os.getenv(home), '.gaphor')


# Application wide resources can be stored in the 'resource' like this
#
# >>> resource('myResource', some_value)
#
# If the resource doesn't already exist, it is created, otherwise the existing
# resource is returned.
resource = Resource(initial_resources={
                        'Name': 'gaphor',
                        'UserDataDir': user_data_dir,
                        'ui.toolbox.classes': True,
                    })


class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
            Exception.__init__(self)
            self.args = args


def new_main(gaphor_file=None):
    """
    Not yet used. see main() below.
    """
    from gaphor.application import Application
    Application.init()

    # backwards compatible
    main_window = resource("MainWindow", Application.main_window)

    if gaphor_file:
        main_window.set_filename(gaphor_file)
        main_window.execute_action('FileRevert')
    else:
        main_window.execute_action('FileNew')
    Application.run()
    Application.shutdown()


def main(gaphor_file=None):
    """
    Start the interactive application.

    This involves importing plugins and creating the main window.
    """
    import pkg_resources

    resource('Version', pkg_resources.get_distribution('gaphor').version)
    resource('DataDir', os.path.join(pkg_resources.get_distribution('gaphor').location, 'gaphor', 'data'))

    # Import GUI stuff here, since the user might not need all the GUI stuff
    import gtk
    import ui
    import adapters
    import actions
    # Load plugin definitions:
    import services.pluginmanager
    import services.undomanager

    from ui.mainwindow import MainWindow

    resource('PluginManager').init(None)

    ui.load_accel_map()

    # should we set a default icon here or something?
    main_window = resource(MainWindow)
    main_window.construct()

    # When the state changes to CLOSED, quit the application
    main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and gtk.main_quit())

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

