# vim: sw=4
"""
File menu related commands.
NewCommand
OpenCommand
SaveCommand
SaveAsCommand
QuitCommand
"""

from gaphor.misc.command import Command
from gaphor.misc.storage import Storage
from commandinfo import CommandInfo
import sys
import gtk
import gaphor.UML as UML
import gaphor.diagram as diagram
import gc

DEFAULT_EXT='.gaphor'

class NewCommand(Command):

    def execute(self):
	fact = GaphorResource(UML.ElementFactory)
	fact.flush()
	gc.collect()
	model = fact.create(UML.Model)
	diagram = fact.create(UML.Diagram)
	diagram.namespace = model
	diagram.name='main'

CommandInfo (name='FileNew', _label='_New', pixname='New',
	     _tip='Create a new Gaphor project',
	     context='main.menu',
	     command_class=NewCommand).register()


class OpenCommand(Command):

    def __init__(self):
	Command.__init__(self)
	self.filename = None

    def execute(self):
	filesel = gtk.FileSelection('Open Gaphor file')
	filesel.hide_fileop_buttons()
	
	if self.filename:
	    filesel.set_filename(self.filename)

	filesel.ok_button.connect('clicked', self.on_ok_button_pressed, filesel)
	filesel.cancel_button.connect('clicked',
				      self.on_cancel_button_pressed, filesel)
	
	filesel.show()
	gtk.main()

    def on_ok_button_pressed(self, button, filesel):
	filename = filesel.get_filename()
	filesel.destroy()
	if filename and len(filename) > 0:
	    self.filename = filename
	    log.debug('Loading from: %s' % filename)
	    GaphorResource(UML.ElementFactory).flush()
	    #GaphorResource(diagram.DiagramItemFactory).flush()

	    gc.collect()

	    store = Storage()
	    try:
		store.load(filename)
	    except Exception, e:
		import traceback
		log.error('Error while loading model from file %s: %s' % (filename, e))
		traceback.print_exc()
	gtk.main_quit()

    def on_cancel_button_pressed(self, button, filesel):
	filesel.destroy()
        gtk.main_quit()

CommandInfo (name='FileOpen', _label='_Open...', pixname='Open', accel='F3',
	     _tip='Load a Gaphor project from a file',
	     context='main.menu',
	     command_class=OpenCommand).register()


class SaveCommand(Command):

    def __init__(self):
	Command.__init__(self)
	self.filename = None

    def execute(self):
	filesel = gtk.FileSelection('Save file')
	if self.filename:
	    filesel.set_filename(self.filename)

	filesel.ok_button.connect('clicked', self.on_ok_button_pressed, filesel)
	filesel.cancel_button.connect('clicked',
				      self.on_cancel_button_pressed, filesel)
	
	filesel.show()
	gtk.main()

    def on_ok_button_pressed(self, button, filesel):
	filename = filesel.get_filename()
	filesel.destroy()
	if filename and len(filename) > 0:
	    if not filename.endswith(DEFAULT_EXT):
		filename = filename + DEFAULT_EXT
	    self.filename = filename
	    log.debug('Saving to: %s' % filename)
	    store = Storage()
	    try:
		store.save(filename)
	    except Exception, e:
		log.error('Error while saving model to file %s: %s' % (filename, e))
	gtk.main_quit()

    def on_cancel_button_pressed(self, button, filesel):
	filesel.destroy()
        gtk.main_quit()

CommandInfo (name='FileSave', _label='_Save', pixname='Save',
	     accel='*Control*s',
	     _tip='Save the current gaphor project',
	     context='main.menu',
	     command_class=SaveCommand).register()


class SaveAsCommand(Command):

    def is_valid(self):
	return SaveCommand().is_valid()

    def execute(self):
	SaveCommand().execute()

CommandInfo (name='FileSaveAs', _label='_Save as...', pixname='Save As',
	     _tip='Save the current gaphor project',
	     context='main.menu',
	     command_class=SaveAsCommand).register()


class RevertCommand(Command):

    def execute(self):
	pass

class QuitCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	import gc
	log.debug('Quiting gaphor...')
	self._window.close()
	del self._window
	gc.collect()

CommandInfo (name='FileQuit', _label='_Quit', pixname='Exit',
	     accel='*Control*q',
	     _tip='Quit Gaphor',
	     context='main.menu',
	     command_class=QuitCommand).register()

class CreateDiagramCommand(Command):

    def execute(self):
	elemfact = GaphorResource(UML.ElementFactory)
	model = elemfact.lookup(1) # model
	diagram = elemfact.create(UML.Diagram)
	diagram.namespace = model
	diagram.name = "New diagram"

CommandInfo (name='CreateDiagram', _label='_New diagram', pixname='gaphor-diagram',
	     _tip='Create a new diagram at toplevel',
	     context='main.menu',
	     command_class=CreateDiagramCommand).register()


class AboutCommand(Command):

    def execute(self):
	import gnome.ui
	import gaphor.config as config
	logo = gtk.gdk.pixbuf_new_from_file (config.DATADIR + '/pixmaps/logo.png')
	about = gnome.ui.About(name = 'Gaphor',
			   version = config.VERSION,
			   copyright = 'Copyright (c) 2001-2002 Arjan J. Molenaar',
			   comments = 'UML Modeling for GNOME',
			   authors = ('Arjan J. Molenaar <arjanmolenaar@hetnet.nl>',),
			   logo_pixbuf = logo)
	about.show()

CommandInfo (name='About', _label='_About...', pixname='About',
	     _tip='About Gaphor',
	     context='main.menu',
	     command_class=AboutCommand).register()

