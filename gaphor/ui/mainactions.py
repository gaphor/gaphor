# vim: sw=4
"""
Main window actions.
"""

from gaphor.misc.action import Action, CheckAction, RadioAction, register_action
import sys
import gobject
import gtk
import gaphor.UML as UML
import gaphor.diagram as diagram
import gc
import traceback
import gaphor

DEFAULT_EXT='.gaphor'

class NewAction(Action):
    id = 'FileNew'
    label = '_New'
    tooltip = 'Create a new Gaphor project'
    stock_id = 'gtk-new'

    def init(self, window):
	self._window = window

    def execute(self):
	factory = gaphor.resource(UML.ElementFactory)
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
	self._window.get_view().expand_row(self._window.get_model().path_from_element(model), False)

register_action(NewAction)


class OpenAction(Action):

    id = 'FileOpen'
    label = '_Open...'
    stock_id='gtk-open'
    tooltip = 'Load a Gaphor project from a file'

    def init(self, window):
	self.filename = None
	self._window = window

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
	    if filename:
		log.debug('Loading from: %s' % filename)
		self.filename = filename
		gc.collect()

		try:
		    import gaphor.storage as storage
		    storage.load(filename)
		    self._window.set_filename(filename)
		    self._window.set_message('Model loaded successfully')
		    model = self._window.get_model()
		    view = self._window.get_view()

		    # Expand all root elements:
		    for node in model.root[1]:
			view.expand_row(model.path_from_element(node[0]), False)

		except Exception, e:
		    import traceback
		    log.error('Error while loading model from file %s: %s' % (filename, e))
		    traceback.print_exc()
	filesel.destroy()

register_action(OpenAction)


class SaveAction(Action):
    id = 'FileSave'
    stock_id = 'gtk-save'

    def init(self, window):
	self._window = window
	self.factory = gaphor.resource('ElementFactory')
	self.factory.connect(self.on_element_factory)
	self.on_element_factory(self)
	# Disconnect when the window is closed:
	window.connect(self.on_window_closed)

    def on_element_factory(self, *args):
	factory = self.factory
	if factory.values():
	    self.sensitive = True
	else:
	    self.sensitive = False

    def on_window_closed(self, window):
	if self._window.get_state() == self._window.STATE_CLOSED:
	    self.factory.disconnect(self.on_element_factory)

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

register_action(SaveAction)


class SaveAsAction(Action):
    id = 'FileSaveAs'
    stock_id = 'gtk-save-as'

    def init(self, window):
	self._window = window
	factory = gaphor.resource('ElementFactory')
	factory.connect(self.on_element_factory)
	self.on_element_factory(self)

    def on_element_factory(self, *args):
	factory = gaphor.resource('ElementFactory')
	if factory.values():
	    self.sensitive = True
	else:
	    self.sensitive = False

    def execute(self):
	filesel = gtk.FileSelection('Save file as')
	response = filesel.run()
	filesel.hide()
	main = gobject.main_context_default()
	while main.pending():
	    main.iteration(False)
	filename = None
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

register_action(SaveAsAction)


class QuitAction(Action):
    id = 'FileQuit'
    stock_id = 'gtk-quit'
    tooltip='Quit Gaphor'

    def init(self, window):
	self._window = window

    def execute(self):
	log.debug('Quiting gaphor...')
	self._window.close()
	del self._window
	gc.collect()

register_action(QuitAction)


class OpenEditorWindowAction(Action):
    id = 'OpenEditorWindow'
    label = '_Editor'
    tooltip = 'Open the Gaphor Editor'

    def init(self, window):
	self._window = window

    def execute(self):
	from gaphor.ui import EditorWindow
	
	ew = EditorWindow()
	ew.construct()
	self._window.add_transient_window(ew)
	self._window.set_message('Editor launched')

register_action(OpenEditorWindowAction)

class OpenConsoleWindowAction(Action):
    id = 'OpenConsoleWindow'
    label = '_Console'
    tooltip = 'Open the Gaphor Console'

    def init(self, window):
	self._window = window

    def execute(self):
	from gaphor.ui.consolewindow import ConsoleWindow
	
	ew = ConsoleWindow()
	ew.construct()
	self._window.add_transient_window(ew)
	self._window.set_message('Console launched')

register_action(OpenConsoleWindowAction)


class AboutAction(Action):
    id = 'About'
    label = '_About'
    tooltip='About Gaphor'
    
    def init(self, window):
	self._window = window

    def execute(self):
	import gnome.ui
	logo = gtk.gdk.pixbuf_new_from_file (gaphor.resource('DataDir') + '/pixmaps/logo.png')
	about = gnome.ui.About(name = 'Gaphor',
			   version = gaphor.resource('Version'),
			   copyright = 'Copyright (c) 2001-2003 Arjan J. Molenaar',
			   comments = 'UML Modeling for GNOME',
			   authors = ('Arjan J. Molenaar <arjanmolenaar@hetnet.nl>',),
			   logo_pixbuf = logo)
	about.show()

register_action(AboutAction)


class CreateDiagramAction(Action):
    id = 'CreateDiagram'
    label = '_New diagram'
    stock_id = 'gaphor-diagram'

    def init(self, window):
	self._window = window

    def update(self):
	element = self._window.get_view().get_selected_element()
	print 'OpenElementAction', element
	self.sensitive = isinstance(element, UML.Package)

    def execute(self):
	element = self._window.get_view().get_selected_element()
	diagram = gaphor.resource('ElementFactory').create(UML.Diagram)
	diagram.package = element

register_action(CreateDiagramAction, 'SelectRow')


class OpenElementAction(Action):
    id = 'OpenModelElement'
    label = '_Open'

    def init(self, window):
	self._window = window

    def update(self):
	element = self._window.get_view().get_selected_element()
	print 'OpenElementAction', element
	self.sensitive = isinstance(element, UML.Diagram)

    def execute(self):
	element = self._window.get_view().get_selected_element()
	if isinstance(element, UML.Diagram):
	    # Import here to avoid cyclic references
	    from gaphor.ui import DiagramWindow
	    newwin = DiagramWindow()
	    newwin.set_diagram(element)
	    newwin.construct()
	    self._window.add_transient_window(newwin)
	else:
	    log.debug('No action defined for element %s' % element.__class__.__name__)

register_action(OpenElementAction, 'SelectRow')


class RenameElementAction(Action):
    id = 'RenameModelElement'
    label = '_Rename'

    def init(self, window):
	self._window = window

    def execute(self):
	view = self._window.get_view()
	selection = view.get_selection()
	model, iter = selection.get_selected()
	if not iter:
	    return
	element = model.get_value(iter, 0)
	path = model.path_from_element(element)
	column = view.get_column(0)
	cell = column.get_cell_renderers()[1]
	cell.set_property('editable', 1)
	cell.set_property('text', element.name)
	view.set_cursor(path, column, True)
	cell.set_property('editable', 0)

register_action(RenameElementAction)


class DeleteCommand(Action):
    """Delete a model element through the tree view. This is only applicable
    to Diagram's and is not undoable."""
    id = 'DeleteElement'
    label = '_Delete'

    def set_parameters(self, params):
	self._window = params['window']
	#self._element = params['element']

    def execute(self):
	pass
	#if isinstance(self._element, UML.Diagram):
	#    self._element.unlink()

class SelectRowAction(Action):
    id = 'SelectRow'

    def init(self, window):
	pass

    def execute(self):
	print self.id

register_action(SelectRowAction)

