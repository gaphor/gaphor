#!/usr/bin/env python

#
# GModeler main application
#
# vim:sw=4

import UML
import ui
import gtk
import gnome.ui

print "TODO: create main application"

class Gaphor:
    def __init__(self):
	self.app = gnome.ui.GnomeApp()
	self.app.show()

    def main(self):
	gtk.main()


app = Gaphor()
app.main()

