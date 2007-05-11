#!/usr/bin/env python
# vim:sw=4
"""This is Gaphor, a Python based UML editor.
"""

__all__ = [ 'main', 'GaphorError' ]

import os

import misc.logger

if os.name == 'nt':
    home = 'USERPROFILE'
else:
    home = 'HOME'

user_data_dir = os.path.join(os.getenv(home), '.gaphor')


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

    from gaphor.application import Application
    Application.init()

    main_window = Application.get_service('gui_manager').main_window
    action_manager = Application.get_service('action_manager')
    if gaphor_file:
        main_window.set_filename(gaphor_file)
        action_manager.execute('file-revert')
    else:
        action_manager.execute('file-new')
    Application.run()
    Application.shutdown()


# TODO: Remove this
import __builtin__
__builtin__.__dict__['log'] = misc.logger.Logger()

if __debug__: 
    refs = []

