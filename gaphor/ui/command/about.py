# vim: sw=4

from gaphor.misc.command import Command
import gtk
import gnome.ui
import gaphor.config as config

class AboutCommand(Command):

    def execute(self):
	logo = gtk.gdk.pixbuf_new_from_file (config.DATADIR + '/pixmaps/logo.png')
	about = gnome.ui.About(name = 'Gaphor',
			   version = config.VERSION,
			   copyright = 'Copyright (c) 2001-2002 Arjan J. Molenaar',
			   comments = 'UML Modeling for GNOME',
			   authors = ('Arjan J. Molenaar <arjanmolenaar at hetnet.nl>',),
			   logo_pixbuf = logo)
	about.show()
