#!/usr/bin/env python

"""This is Gaphor, a Python+GTK based UML modelling tool.

This module allows Gaphor to be launched from the command line.
The main() function sets up the command-line options and arguments and
passes them to the main Application instance."""

__all__ = [ 'main' ]

from optparse import OptionParser
import pygtk

from gaphor.misc.logger import Logger
from gaphor.application import Application

pygtk.require('2.0')


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
                      '--profile',\
                      action='store_true',\
                      help='Run in profile')

    parser.add_option('-l',\
                      '--logging',\
                      default='INFO',\
                      help='Logging level')
                      
    options, args = parser.parse_args()
    
    Logger.log_level = Logger.level_map[options.logging]

    try:
        model = args[1]
    except IndexError:
        model = None

    if options.profile:

        import cProfile
        import pstats

        cProfile.run('import gaphor; gaphor.launch()',\
                     'gaphor.prof')
        
        profile_stats = pstats.Stats('gaphor.prof')
        profile_stats.strip_dirs().sort_stats('time').print_stats(50)

    else:
	
        launch(model)

# TODO: Remove this.  
import __builtin__

__builtin__.__dict__['log'] = Logger()

# vim:sw=4:et:ai
