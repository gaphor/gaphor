#!/usr/bin/env python

#
# Gaphor main application
#
# vim:sw=4

from misc.singleton import Singleton
import config

class Gaphor(Singleton):
    NAME='gaphor'
    VERSION=config.GAPHOR_VERSION
    TITLE='Gaphor v' + VERSION

    def init(self):
	import gnome
	import ui
	gnome.program_init(Gaphor.NAME, Gaphor.VERSION)
	self.__mainwindow = ui.MainWindow(Gaphor.NAME, Gaphor.TITLE)

    def main(self):
	import gtk
	gtk.main()

    def get_mainwindow(self):
        return self.__mainwindow
