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
resource = Resource(initial_resources={ })


class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
            Exception.__init__(self)
            self.args = args


def main(gaphor_file=None):
    """
    Start the main application by initiating and running
    gaphor.application.Application. 
    """
    import pkg_resources

    resource('DataDir', os.path.join(pkg_resources.get_distribution('gaphor').location, 'gaphor', 'data'))

    from gaphor.application import Application
    Application.init()

    main_window = Application.get_service('gui_manager').main_window
    action_manager = Application.get_service('action_manager')
    if gaphor_file:
        main_window.set_filename(gaphor_file)
        action_manager.execute('FileRevert')
    else:
        action_manager.execute('FileNew')
    Application.run()
    Application.shutdown()


# TODO: Remove this
import __builtin__
__builtin__.__dict__['log'] = misc.logger.Logger()

if __debug__: 
    refs = []

