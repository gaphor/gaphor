#!/usr/bin/env python

#
# GModeler main application
#
# vim:sw=4

from misc.singleton import Singleton

class Gaphor(Singleton):
    NAME='gaphor'
    TITLE='Gaphor v0.1'

    def __init__(self):
	#self.app = gnome.ui.MDI(Gaphor.NAME, Gaphor.TITLE)
	#view = gnome.ui.MDIGenericChild('window1')
	#self.app.add_view(view)
	pass

    def main(self):
	gtk.main()


#app = Gaphor()
#app.main()

