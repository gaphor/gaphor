#!/usr/bin/env python

# Copyright (C) 2002-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License
# more details.
#
# You should have received a copy of the GNU Library General Public
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
This module allows Gaphor to be launched from the command line.
The main() function sets up the command-line options and arguments and
passes them to the main Application instance.
"""

from __future__ import absolute_import

import logging
import pygtk
from optparse import OptionParser
import six.moves.builtins

from gaphor.application import Application

pygtk.require('2.0')

LOG_FORMAT = '%(name)s %(levelname)s %(message)s'

__all__ = ['main']


def launch(model=None):
    """Start the main application by initiating and running Application.
    
    The file_manager service is used here to load a Gaphor model if one was
    specified on the command line.  Otherwise, a new model is created and
    the Gaphor GUI is started."""

    # Make sure gui is loaded ASAP.
    # This prevents menu items from appearing at unwanted places.
    Application.essential_services.append('main_window')

    Application.init()

    main_window = Application.get_service('main_window')

    main_window.open()

    file_manager = Application.get_service('file_manager')

    if model:
        file_manager.load(model)
    else:
        file_manager.action_new()

    Application.run()


def main():
    """Start Gaphor from the command line.  This function creates an option
    parser for retrieving arguments and options from the command line.  This
    includes a Gaphor model to load.
    
    The application is then initialized, passing along the option parser.  This
    provides and plugins and services with access to the command line options
    and may add their own."""

    parser = OptionParser()

    parser.add_option('-p', '--profiler', action='store_true', help='Run in profiler')
    parser.add_option('-q', "--quiet", dest='quiet', help='Quiet output', default=False, action='store_true')
    parser.add_option('-v', '--verbose', dest='verbose', help='Verbose output', default=False, action="store_true")

    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    elif options.quiet:
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    try:
        model = args[0]
    except IndexError:
        model = None

    if options.profiler:

        import cProfile
        import pstats

        cProfile.run('import gaphor; gaphor.launch()', 'gaphor.prof')

        profile_stats = pstats.Stats('gaphor.prof')
        profile_stats.strip_dirs().sort_stats('time').print_stats(50)

    else:

        launch(model)


# TODO: Remove this.

six.moves.builtins.__dict__['log'] = logging.getLogger('Gaphor')

# vim:sw=4:et:ai
