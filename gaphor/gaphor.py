#!/usr/bin/env python

#
# Gaphor main application
#
# vim:sw=4

from misc.singleton import Singleton
import config
import gettext

class Gaphor(Singleton):
    """
    Gaphor main app.
    """
    NAME='gaphor'
    VERSION=config.VERSION
    TITLE='Gaphor v' + VERSION

    def init(self):
	gettext.install(config.GETTEXT_PACKAGE)
	self.__main_window = None
	pass

    def main(self):
	from gtk import main as _main
	from gnome import program_init
	from ui import MainWindow
	program_init(Gaphor.NAME, Gaphor.VERSION)
	self.__main_window = MainWindow(Gaphor.NAME, Gaphor.TITLE)
	_main()

    def get_main_window(self):
        return self.__main_window
