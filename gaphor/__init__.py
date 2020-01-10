#!/usr/bin/env python

"""Gaphor is the simple modeling tool written in Python.

This module allows Gaphor to be launched from the command line.
The main() function sets up the command-line options and arguments and
passes them to the main Application instance.

"""
# Examples of valid version strings
# __version__ = '1.2.3.dev1'  # Development release 1
# __version__ = '1.2.3a1'     # Alpha Release 1
# __version__ = '1.2.3b1'     # Beta Release 1
# __version__ = '1.2.3rc1'    # RC Release 1
# __version__ = '1.2.3'       # Final Release
# __version__ = '1.2.3.post1' # Post Release 1

__version__ = "1.1.1"
__all__ = ["main"]

import logging
from optparse import OptionParser

from gaphor.application import Application

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main():
    """Start Gaphor from the command line.  This function creates an option
    parser for retrieving arguments and options from the command line.  This
    includes a Gaphor model to load.

    The application is then initialized, passing along the option parser.  This
    provides plugins and services with access to the command line options
    and may add their own."""

    import sys
    import gaphor.ui

    def has_option(*options):
        return any(o in sys.argv for o in options)

    if has_option("-v", "--verbose"):
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    elif has_option("-q", "--quiet"):
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    if has_option("-p", "--profiler"):

        import cProfile
        import pstats

        cProfile.runctx(
            "gaphor.ui.run(Application, sys.argv)",
            globals(),
            locals(),
            filename="gaphor.prof",
        )

        profile_stats = pstats.Stats("gaphor.prof")
        profile_stats.strip_dirs().sort_stats("time").print_stats(50)

    else:
        gaphor.ui.run(Application, sys.argv)
