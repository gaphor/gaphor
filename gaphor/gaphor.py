#!/usr/bin/env python

#
# GModeler main application
#
# vim:sw=4

from misc.singleton import Singleton
import gtk
import gnome
import gnome.ui
import ui

class Gaphor(Singleton):
    NAME='gaphor'
    VERSION='0.1'
    TITLE='Gaphor v' + VERSION

    def init(self):
	#gnome.init(Gaphor.NAME, Gaphor.VERSION + 
	self.app = gnome.ui.App(Gaphor.NAME, Gaphor.TITLE)
	self.app_bar = gnome.ui.AppBar (0, 1, gnome.ui.USER)
	self.app.set_menubar(self.app_bar)
	#view = gnome.ui.MDIGenericChild('window1')
	#self.app.add_view(view)
	pass

    def main(self):
	gtk.main()


#app = Gaphor()
#app.main()

