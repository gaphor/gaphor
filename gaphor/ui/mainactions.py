# vim: sw=4:et
"""
Main window actions.
"""

import sys
import gobject
import gtk
import gaphor.UML as UML
import gaphor.diagram as diagram
import gc
import traceback
from threading import Thread

import gaphor
from gaphor.misc.action import Action, CheckAction, RadioAction, register_action
from gaphor.misc.gidlethread import GIdleThread, Queue, QueueEmpty
from gaphor.i18n import _

DEFAULT_EXT='.gaphor'

def show_status_window(title, message, parent=None, queue=None):
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title(title)
    win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
    win.set_transient_for(parent)
    win.set_modal(True)
    win.set_resizable(False)
    win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
    win.set_skip_taskbar_hint(True)
    win.set_skip_pager_hint(True)
    win.set_border_width(24)
    vbox = gtk.VBox(spacing=24)
    win.add(vbox)
    label = gtk.Label(message)
    label.set_padding(8,8)
    vbox.pack_start(label)
    progress_bar = gtk.ProgressBar()
    vbox.pack_start(progress_bar, expand=False, fill=False, padding=0)

    def progress_idle_handler(progress_bar, queue):
        #print '.',
        percentage = 0
        try:
            while True:
                percentage = queue.get()
        except QueueEmpty:
            pass
        if percentage:
            progress_bar.set_fraction(percentage / 100.0)
        return True

    if queue:
        idle_id = gobject.idle_add(progress_idle_handler, progress_bar, queue,
                                   priority=gobject.PRIORITY_LOW)
        # Make sure the idle fucntion is removed as soon as the window
        # is destroyed.
        def remove_progress_idle_handler(window, idle_id):
            #print 'remove_progress_idle_handler', idle_id
            gobject.source_remove(idle_id)
        win.connect('destroy', remove_progress_idle_handler, idle_id)

    win.show_all()
    return win

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
        #stereotypes = factory.create(UML.Profile)
        #stereotypes.name = 'Stereotypes'
        self._window.set_filename(None)
        self._window.set_message(_('Created a new model'))
        factory.notify_model()

        self._window.select_element(diagram)
        self._window.execute_action('OpenModelElement')

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
        filename = filesel.get_filename()
        filesel.destroy()
        if filename and response == gtk.RESPONSE_OK:
            action_states = self._window.action_pool.get_action_states()
            try:
                import gaphor.storage as storage
                log.debug('Loading from: %s' % filename)
                queue = Queue()
                win = show_status_window(_('Loading...'), _('Loading model from %s') % filename, self._window.get_window(), queue)
                self.filename = filename
                gc.collect()
                worker = GIdleThread(storage.load_generator(filename), queue)
                self._window.action_pool.insensivate_actions()
                worker.start()
                worker.wait()
                if worker.error:
                    log.error('Error while loading model from file %s: %s' % (filename, worker.error))

                self._window.set_filename(filename)
                self._window.set_message('Model loaded successfully')
                model = self._window.get_model()
                view = self._window.get_tree_view()

                # Expand all root elements:
                for node in model.root[1]:
                    view.expand_row(model.path_from_element(node[0]), False)

                # Restore states of actions
                win.destroy()
            finally:
                self._window.action_pool.set_action_states(action_states)
                self._window.action_pool.update_actions()

register_action(OpenAction)


class SaveAsAction(Action):
    id = 'FileSaveAs'
    stock_id = 'gtk-save-as'

    def init(self, window):
        self._window = window
        self.factory = gaphor.resource('ElementFactory')
        self.factory.connect(self.on_element_factory)
        self.on_element_factory(self)
        # Disconnect when the window is closed:
        window.connect(self.on_window_closed)

    def on_element_factory(self, *args):
        #factory = gaphor.resource('ElementFactory')
        if self.factory.values():
            self.sensitive = True
        else:
            self.sensitive = False

    def on_window_closed(self, window):
        if self._window.get_state() == self._window.STATE_CLOSED:
            self.factory.disconnect(self.on_element_factory)

    def save(self, filename):
        if filename and len(filename) > 0:
            import gaphor.storage as storage
            if not filename.endswith(DEFAULT_EXT):
                filename = filename + DEFAULT_EXT

            queue = Queue()
            log.debug('Saving to: %s' % filename)
            win = show_status_window('Saving...', 'Saving model to %s' % filename, self._window.get_window(), queue)
            worker = GIdleThread(storage.save_generator(filename), queue)
            action_states = self._window.action_pool.get_action_states()
            self._window.action_pool.insensivate_actions()
            worker.start()
            worker.wait()
            if worker.error:
                log.error('Error while saving model to file %s: %s' % (filename, worker.error))

            self._window.set_filename(filename)

            # Restore states of actions
            self._window.action_pool.set_action_states(action_states)
            win.destroy()

    def execute(self):
        filename = self._window.get_filename()
        filesel = gtk.FileSelection('Save file as')
        filesel.set_filename(filename or '')
        response = filesel.run()
        filename = None
        if response == gtk.RESPONSE_OK:
            filename = filesel.get_filename()
        filesel.destroy()
        self.save(filename)

register_action(SaveAsAction)


class SaveAction(SaveAsAction):
    id = 'FileSave'
    stock_id = 'gtk-save'

    def execute(self):
        filename = self._window.get_filename()
        if filename:
            self.save(filename)
        else:
            SaveAsAction.execute(self)

register_action(SaveAction)


class CloseAction(Action):
    id = 'FileClose'
    stock_id = 'gtk-close'
    tooltip='Close the diagram window'

    def init(self, window):
        self._window = window

    def execute(self):
        self._window.close()

register_action(CloseAction)


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
        from gaphor.ui.editorwindow import EditorWindow
        
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
    stock_id = 'gtk-about'
    tooltip='About Gaphor'
    
    def init(self, window):
        self._window = window

    def execute(self):
        logo = gtk.gdk.pixbuf_new_from_file (gaphor.resource('DataDir') + '/pixmaps/logo.png')
        version = gaphor.resource('Version')
        about = gtk.Dialog("About Gaphor", self._window.get_window(), gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
        about.set_default_response(gtk.RESPONSE_OK)
        vbox = about.vbox

        image = gtk.Image()
        image.set_from_pixbuf(logo)
        vbox.pack_start(image)

        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        #notebook.set_show_border(False)
        notebook.set_border_width(4)
        notebook.set_tab_pos(gtk.POS_BOTTOM)
        vbox.pack_start(notebook)

        tab_vbox = gtk.VBox()

        def add_label(text, padding_x=0, padding_y=0):
            label = gtk.Label(text)
            label.set_property('use-markup', True)
            label.set_padding(padding_x, padding_y)
            label.set_justify(gtk.JUSTIFY_CENTER)
            tab_vbox.pack_start(label)

        #add_label('<span size="xx-large" weight="bold">Gaphor</span>')
        add_label('<span weight="bold">version %s</span>' % version)
        add_label('<span variant="smallcaps">UML Modeling tool for GNOME</span>', 8, 8)
        add_label('<span size="small">Copyright (c) 2001-2004 Arjan J. Molenaar</span>', 8, 8)
        #vbox.pack_start(gtk.HSeparator())
        notebook.append_page(tab_vbox, gtk.Label('About'))

        tab_vbox = gtk.VBox()
        
        add_label('This software is published\n'
                  'under the terms of the\n'
                  '<span weight="bold">GNU General Public License v2</span>.\n'
                  'See the COPYING file for details.', 0, 8)
        notebook.append_page(tab_vbox, gtk.Label('License'))

        tab_vbox = gtk.VBox()
        
        add_label('Gaphor is written by:\n'
                  'Arjan Molenaar\n'
                  'Jeroen Vloothuis\n'
                  'wrobell')
        add_label('')
        notebook.append_page(tab_vbox, gtk.Label('Authors'))

        vbox.show_all()
        about.run()
        about.destroy()

register_action(AboutAction)


class CreateDiagramAction(Action):
    id = 'CreateDiagram'
    label = '_New diagram'
    stock_id = 'gaphor-diagram'

    def init(self, window):
        self._window = window

    def update(self):
        element = self._window.get_tree_view().get_selected_element()
        self.sensitive = isinstance(element, UML.Package)

    def execute(self):
        element = self._window.get_tree_view().get_selected_element()
        diagram = gaphor.resource('ElementFactory').create(UML.Diagram)
        diagram.package = element

        self._window.select_element(diagram)
        self._window.execute_action('OpenModelElement')

register_action(CreateDiagramAction, 'SelectRow')


class DeleteDiagramAction(Action):
    id = 'DeleteDiagram'
    label = '_Delete diagram'
    stock_id = 'gtk-delete'

    def init(self, window):
        self._window = window

    def update(self):
        element = self._window.get_tree_view().get_selected_element()
        self.sensitive = isinstance(element, UML.Diagram)

    def execute(self):
        diagram = self._window.get_tree_view().get_selected_element()
        assert isinstance(diagram, UML.Diagram)
        m = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
                              gtk.BUTTONS_YES_NO,
                              'Do you really want to delete diagram %s?\n\n'
                              'This will possibly delete diagram items\n'
                              'that are not shown in other diagrams.\n'
                              'This operation is not undoable!' \
                              % (diagram.name or '<None>'))
        if (m.run() == gtk.RESPONSE_YES):
            diagram.unlink()
        m.destroy()

register_action(DeleteDiagramAction, 'SelectRow')


class OpenElementAction(Action):
    id = 'OpenModelElement'
    label = '_Open'

    def init(self, window):
        self._window = window

    def update(self):
        element = self._window.get_tree_view().get_selected_element()
        self.sensitive = isinstance(element, UML.Diagram)

    def execute(self):
        element = self._window.get_tree_view().get_selected_element()
        if isinstance(element, UML.Diagram):
            self._window.show_diagram(element)
        else:
            log.debug('No action defined for element %s' % type(element).__name__)

register_action(OpenElementAction, 'SelectRow')


class RenameElementAction(Action):
    id = 'RenameModelElement'
    label = '_Rename'

    def init(self, window):
        self._window = window

    def execute(self):
        view = self._window.get_tree_view()
        element = view.get_selected_element()
        #model, iter = selection.get_selected()
        #if not iter:
            #return
        #element = model.get_value(iter, 0)
        path = view.get_model().path_from_element(element)
        column = view.get_column(0)
        cell = column.get_cell_renderers()[1]
        cell.set_property('editable', 1)
        cell.set_property('text', element.name)
        view.set_cursor(path, column, True)
        cell.set_property('editable', 0)

register_action(RenameElementAction)


class RefreshNamespaceModelAction(Action):

    """Delete a model element through the tree view. This is only applicable
    to Diagram's and is not undoable."""
    id = 'RefreshNamespaceModel'
    label = '_Refresh'

    def init(self, window):
        self._window = window

    def execute(self):
        self._window.get_model().refresh()

register_action(RefreshNamespaceModelAction)


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
        pass

register_action(SelectRowAction)


class TabChangeAction(Action):
    id = 'TabChange'

    def init(self, window):
        pass

register_action(TabChangeAction)
