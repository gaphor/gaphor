#!/usr/bin/env python

"""This is Gaphor, a Python+GTK based UML modelling tool.

This module allows Gaphor to be launched from the command line.
The main() function sets up the command-line options and arguments and
passes them to the main Application instance."""

from __future__ import absolute_import
__all__ = [ 'main' ]

from optparse import OptionParser
import logging
import pygtk

from gaphor.application import Application

pygtk.require('2.0')

LOG_FORMAT = '%(name)s %(levelname)s %(message)s'


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

    parser.add_option('-p',\
                      '--profiler',\
                      action='store_true',\
                      help='Run in profiler')
    parser.add_option('-q', "--quiet",
                      dest='quiet', help='Quiet output',
                      default=False, action='store_true')
    parser.add_option('-v', '--verbose',
                      dest='verbose', help='Verbose output',
                      default=False, action="store_true")
    
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

        cProfile.run('import gaphor; gaphor.launch()',\
                     'gaphor.prof')
        
        profile_stats = pstats.Stats('gaphor.prof')
        profile_stats.strip_dirs().sort_stats('time').print_stats(50)

    else:
	
        launch(model)

# TODO: Remove this.  
import six.moves.builtins

six.moves.builtins.__dict__['log'] = logging.getLogger('Gaphor')

# vim:sw=4:et:ai
