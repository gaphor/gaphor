# vim: sw=4
"""
File menu related commands.
NewCommand
OpenCommand
SaveCommand
SaveAsCommand
QuitCommand
"""

from commandinfo import Command, CommandInfo
import sys
import gobject
import gtk
import gaphor.UML as UML
import gaphor.diagram as diagram
import gc
import traceback

DEFAULT_EXT='.gaphor'

class NewCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	factory = GaphorResource(UML.ElementFactory)
	factory.flush()
	gc.collect()
	model = factory.create(UML.Package)
	model.name = 'New model'
	diagram = factory.create(UML.Diagram)
	diagram.package = model
	diagram.name='main'
	self._window.set_filename(None)
	self._window.set_message('Created a new model')
	factory.notify_model()

CommandInfo (name='FileNew', _label='_New', pixname='New',
	     _tip='Create a new Gaphor project',
	     context='main.menu',
	     command_class=NewCommand).register()


class OpenCommand(Command):

    def __init__(self):
	Command.__init__(self)
	self.filename = None

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	filesel = gtk.FileSelection('Open Gaphor file')
	filesel.hide_fileop_buttons()
	filesel.set_filename(self.filename or '')

	response = filesel.run()
	filesel.hide()
	main = gobject.main_context_default()
	while main.pending():
	    main.iteration(False)
	if response == gtk.RESPONSE_OK:
	    filename = filesel.get_filename()
	    if filename and len(filename) > 0:
		log.debug('Loading from: %s' % filename)
		self.filename = filename
		gc.collect()

		try:
		    import gaphor.storage as storage
		    storage.load(filename)
		    self._window.set_filename(filename)
		    self._window.set_message('Model loaded successfully')
		except Exception, e:
		    import traceback
		    log.error('Error while loading model from file %s: %s' % (filename, e))
		    traceback.print_exc()
	filesel.destroy()

CommandInfo (name='FileOpen', _label='_Open...', pixname='Open', accel='F3',
	     _tip='Load a Gaphor project from a file',
	     context='main.menu',
	     command_class=OpenCommand).register()


class SaveCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	filename = self._window.get_filename()
	if not filename:
	    filesel = gtk.FileSelection('Save file')
	    response = filesel.run()
	    filesel.hide()
	    main = gobject.main_context_default()
	    while main.pending():
		main.iteration(False)
	    if response == gtk.RESPONSE_OK:
		filename = filesel.get_filename()
	    filesel.destroy()
	if filename and len(filename) > 0:
	    if not filename.endswith(DEFAULT_EXT):
		filename = filename + DEFAULT_EXT
	    log.debug('Saving to: %s' % filename)
	    try:
		import gaphor.storage as storage
		storage.save(filename)
		self._window.set_filename(filename)
		self._window.set_message('Model saved to %s' % filename)
	    except Exception, e:
		log.error('Failed to save to file %s: %s' % (filename, e))
		traceback.print_exc()

CommandInfo (name='FileSave', _label='_Save', pixname='Save',
	     accel='*Control*s',
	     _tip='Save the current gaphor project',
	     context='main.menu', sensitive=('model',),
	     command_class=SaveCommand).register()


class SaveAsCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	filesel = gtk.FileSelection('Save file as')
	response = filesel.run()
	filesel.hide()
	main = gobject.main_context_default()
	while main.pending():
	    main.iteration(False)
	if response == gtk.RESPONSE_OK:
	    filename = filesel.get_filename()
	filesel.destroy()
	if filename and len(filename) > 0:
	    if not filename.endswith(DEFAULT_EXT):
		filename = filename + DEFAULT_EXT
	    log.debug('Saving to: %s' % filename)
	    try:
		import gaphor.storage as storage
		storage.save(filename)
		self._window.set_filename(filename)
	    except Exception, e:
		log.error('Failed to save to file %s: %s' % (filename, e))
		traceback.print_exc()

CommandInfo (name='FileSaveAs', _label='_Save as...', pixname='Save As',
	     _tip='Save the current gaphor project',
	     context='main.menu', sensitive=('model',),
	     command_class=SaveAsCommand).register()


class RevertCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	if self._window.get_filename():
	    log.debug('Loading from: %s' % filename)
	    #GaphorResource(UML.ElementFactory).flush()

	    try:
		import gaphor.storage as storage
		storage.load(filename)
	    except Exception, e:
		import traceback
		log.error('Error while loading model from file %s: %s' % (filename, e))
		traceback.print_exc()

class QuitCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
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
    """Obsolete..."""

    def set_parameters(self, params):
	self._window = params.get('window')
	# in a popup menu?
	self._parent = params.get('element')

    def execute(self):
	elemfact = GaphorResource(UML.ElementFactory)
	diagram = elemfact.create(UML.Diagram)
	if self._parent:
	    diagram.package = self._parent
	diagram.name = "New diagram"
	# TODO: select the diagram
	view = self._window.get_view()
	model = view.get_model()
	sel = view.get_selection()
	path = model.path_from_element(diagram)
	sel.select_path(path)

CommandInfo (name='CreateDiagram', _label='_New diagram', pixname='gaphor-diagram',
	     _tip='Create a new diagram at toplevel',
	     context='main.menu', sensitive=('model',),
	     command_class=CreateDiagramCommand).register()


class OpenEditorWindowCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	from gaphor.ui import EditorWindow
	
	ew = EditorWindow()
	ew.construct()
	self._window.add_transient_window(ew)
	self._window.set_message('Editor launched')

CommandInfo (name='OpenEditorWindow', _label='_Editor...', pixname='Editor',
	     _tip='Open the Gaphor Editor',
	     context='main.menu',
	     command_class=OpenEditorWindowCommand).register()


class AboutCommand(Command):

    def execute(self):
	import gnome.ui
	from gaphor import Gaphor
	logo = gtk.gdk.pixbuf_new_from_file (Gaphor().get_datadir() + '/pixmaps/logo.png')
	about = gnome.ui.About(name = 'Gaphor',
			   version = Gaphor.VERSION,
			   copyright = 'Copyright (c) 2001-2003 Arjan J. Molenaar',
			   comments = 'UML Modeling for GNOME',
			   authors = ('Arjan J. Molenaar <arjanmolenaar@hetnet.nl>',),
			   logo_pixbuf = logo)
	about.show()

CommandInfo (name='About', _label='_About...', pixname='About',
	     _tip='About Gaphor',
	     context='main.menu',
	     command_class=AboutCommand).register()

