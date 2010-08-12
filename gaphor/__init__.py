#!/usr/bin/env python
"""
This is Gaphor, a Python based UML modelling tool.
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


def launch(gaphor_file=None):
    """
    Start the main application by initiating and running
    gaphor.application.Application. 
    """
    import pkg_resources

    from gaphor.application import Application
    Application.init()

    file_manager = Application.get_service('file_manager')
    if gaphor_file:
        file_manager.load(gaphor_file)
    else:
        file_manager.new()

    Application.run()
    #Application.shutdown()


def main():
    """
    Main from the command line
    """

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-p',\
		      '--profile',\
		      action='store_true',\
		      help='Run in profile')

    options, args = parser.parse_args()

    if options.profile:
	print 'Starting profiler...'
        import cProfile
        import pstats
        if len(args)==1:
	    cProfile.run('import gaphor; gaphor.launch("%s")'%args[0],\
            	         'gaphor.prof')
	else:
	    cProfile.run('import gaphor; gaphor.launch()',\
                         'gaphor.prof')
        p = pstats.Stats('gaphor.prof')
        p.strip_dirs().sort_stats('time').print_stats(50)

    elif len(args) == 1:
	launch(args[0])

    else:
	launch()

# TODO: Remove this
import __builtin__
__builtin__.__dict__['log'] = misc.logger.Logger()

if __debug__: 
    refs = []

# vim:sw=4
