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
    NAME='gaphor'
    TITLE='Gaphor v0.1'

    def __init__(self):
	#self.app = gnome.ui.MDI(Gaphor.NAME, Gaphor.TITLE)
	#view = gnome.ui.MDIGenericChild('window1')
	#self.app.add_view(view)
	pass

    def about(self):
	about = gnome.ui.About('Gaphor',
			       '0.1',
			       'Copyright (c) 2001-2002 Arjan J. Molenaar',
			       'UML Modeling for GNOME',
			       ('Arjan J. Molenaar',))
	about.show()
	
    def main(self):
	self.about()
	gtk.main()


app = Gaphor()
app.main()

