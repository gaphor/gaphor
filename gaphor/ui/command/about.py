# vim: sw=4

from gaphor.misc.command import Command
import gnome.ui
import gaphor.config as config

class AboutCommand(Command):

    def execute(self):
	about = gnome.ui.About('Gaphor',
			       config.VERSION,
			       'Copyright (c) 2001-2002 Arjan J. Molenaar',
			       'UML Modeling for GNOME',
			       ('Arjan J. Molenaar',))
	about.show()
	pass
