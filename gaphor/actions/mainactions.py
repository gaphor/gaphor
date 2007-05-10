"""
Main window actions.
"""

import os.path
import sys
import pkg_resources
import gobject
import gtk
import gc
from gaphor.core import inject
from gaphor.application import Application
from gaphor import UML
from gaphor import diagram
from gaphor.misc.action import Action, CheckAction, RadioAction, register_action
from gaphor.misc.action import DynamicMenu, ObjectAction, register_slot
from gaphor.misc.action import ActionError
from gaphor.misc.gidlethread import GIdleThread, Queue, QueueEmpty
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.misc.errorhandler import error_handler, ErrorHandlerAspect, weave_method
from gaphor.i18n import _

DEFAULT_EXT='.gaphor'

def get_undo_manager():
    return Application.get_service('undo_manager')

def show_status_window(title, message, parent=None, queue=None):
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title(title)
    win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
    win.set_transient_for(parent)
    win.set_modal(True)
    win.set_resizable(False)
    win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
    #win.set_skip_taskbar_hint(True)
    #win.set_skip_pager_hint(True)
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
            progress_bar.set_fraction(min(percentage / 100.0, 100.0))
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
    label = _('_New')
    tooltip = 'Create a new Gaphor project'
    stock_id = 'gtk-new'

    element_factory = inject('element_factory')
    action_manager = inject('action_manager')

    def init(self, window):
        self._window = window

    def execute(self):
        element_factory = self.element_factory
        if element_factory.size():
            dialog = gtk.MessageDialog(self._window.get_window(),
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                _("Opening a new model will flush the currently loaded model.\nAny changes made will not be saved. Do you want to continue?"))
            answer = dialog.run()
            dialog.destroy()
            if answer != gtk.RESPONSE_YES:
                return

        element_factory.flush()
        gc.collect()
        model = element_factory.create(UML.Package)
        model.name = _('New model')
        diagram = element_factory.create(UML.Diagram)
        diagram.package = model
        diagram.name='main'
        #stereotypes = element_factory.create(UML.Profile)
        #stereotypes.name = 'Stereotypes'
        self._window.set_filename(None)
        #self._window.set_message(_('Created a new model'))
        element_factory.notify_model()

        self._window.select_element(diagram)
        self.action_manager.execute('OpenModelElement')

weave_method(NewAction.execute, ErrorHandlerAspect, message='Could not create a new model.')
register_action(NewAction)


class RevertAction(Action):
    id = 'FileRevert'
    label = _('_Revert...')
    stock_id='gtk-revert'
    tooltip = 'Reload the loaded Gaphor project from file'

    element_factory = inject('element_factory')
    action_manager = inject('action_manager')

    def init(self, window):
        # The filename of the last file loaded
        self.filename = None
        self._window = window

    def update(self):
        self.sensitive = bool(self._window.get_filename())

    def execute(self):
        filename = self._window.get_filename()
        self.load(filename)

    def load(self, filename):
        #action_states = self._window.action_pool.get_action_states()
        try:
            from gaphor import storage
            log.debug('Loading from: %s' % filename)
            queue = Queue()
            win = show_status_window(_('Loading...'), _('Loading model from %s') % filename, self._window.get_window(), queue)
            self.filename = filename
            gc.collect()
            worker = GIdleThread(storage.load_generator(filename, self.element_factory), queue)
            #self._window.action_pool.insensivate_actions()
            get_undo_manager().clear_undo_stack()
            get_undo_manager().clear_redo_stack()
            worker.start()
            worker.wait()
            if worker.error:
                log.error('Error while loading model from file %s: %s' % (filename, worker.error))
                error_handler(message='Error while loading model from file %s' % filename, exc_info=worker.exc_info)

            #self._window.set_message('Model loaded successfully')
            model = self._window.get_model()
            view = self._window.get_tree_view()

            self._window.set_filename(filename)

            # Expand all root elements:
            for node in model.root[1]:
                view.expand_row(model.path_from_element(node[0]), False)

        finally:
            #self._window.action_pool.set_action_states(action_states)
            self.action_manager.update_actions()
            try:
                win.destroy()
            except:
                pass

weave_method(RevertAction.execute, ErrorHandlerAspect, message=_('Could not load model file.'))
register_action(RevertAction, 'FileNew', 'FileOpen', 'FileSave', 'FileSaveAs')


class OpenAction(RevertAction):

    id = 'FileOpen'
    label = _('_Open...')
    stock_id='gtk-open'
    tooltip = 'Load a Gaphor project from a file'

    def update(self):
        pass

    def execute(self):
        filesel = gtk.FileChooserDialog(title='Open Gaphor model',
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name("Gaphor models")
        filter.add_pattern("*.gaphor")
        filesel.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        filesel.add_filter(filter)

        if self.filename:
            filesel.set_current_name(self.filename)

        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if filename and response == gtk.RESPONSE_OK:
            RevertAction.load(self, filename)

register_action(OpenAction)


class SaveAsAction(Action):
    id = 'FileSaveAs'
    stock_id = 'gtk-save-as'
    tooltip = _('Save the model to a new file')

    element_factory = inject('element_factory')

    def init(self, window):
        self._window = window
        #self.element_factory = self.element_factory
        #self.element_factory.connect(self.on_element_factory)
        #self.on_element_factory(self)
        # Disconnect when the window is closed:
        #window.connect(self.on_window_closed)

    def on_element_factory(self, *args):
        if self.element_factory.values():
            self.sensitive = True
        else:
            self.sensitive = False

    def on_window_closed(self, window):
        if self._window.get_state() == self._window.STATE_CLOSED:
            self.element_factory.disconnect(self.on_element_factory)

    def save(self, filename):
        if filename and len(filename) > 0:
            from gaphor import storage
            if not filename.endswith(DEFAULT_EXT):
                filename = filename + DEFAULT_EXT

            queue = Queue()
            log.debug('Saving to: %s' % filename)
            win = show_status_window('Saving...', 'Saving model to %s' % filename, self._window.get_window(), queue)
            try:
                out = open(filename, 'w')

                worker = GIdleThread(storage.save_generator(XMLWriter(out), self.element_factory), queue)
                #action_states = self._window.action_pool.get_action_states()
                #self._window.action_pool.insensivate_actions()
                worker.start()
                worker.wait()
                if worker.error:
                    log.error('Error while saving model to file %s: %s' % (filename, worker.error))
                    error_handler(message='Error while saving model to file %s' % filename, exc_info=worker.exc_info)
                out.close()

                self._window.set_filename(filename)

                # Restore states of actions
                #self._window.action_pool.set_action_states(action_states)
            finally:
                win.destroy()

    def execute(self):
        filename = self._window.get_filename()
        filesel = gtk.FileChooserDialog(title=_('Save Gaphor model as'),
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        if filename:
            filesel.set_current_name(filename)
        response = filesel.run()
        filename = None
        if response == gtk.RESPONSE_OK:
            filename = filesel.get_filename()
        filesel.destroy()
        self.save(filename)

weave_method(SaveAsAction.save, ErrorHandlerAspect, message='Could not save model to file.')
register_action(SaveAsAction)


class SaveAction(SaveAsAction):
    id = 'FileSave'
    stock_id = 'gtk-save'
    tooltip = 'Save the model to a file'

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
        if self._window.ask_to_close():
            log.debug('Quiting gaphor...')
            self._window.close()
            del self._window
            gc.collect()

register_action(QuitAction)


class OpenEditorWindowAction(Action):
    id = 'OpenEditorWindow'
    label = _('_Editor')
    tooltip = 'Open the Gaphor Editor'

    def init(self, window):
        self._window = window

    def execute(self):
        from gaphor.ui.editorwindow import EditorWindow
        
        ew = EditorWindow()
        ew.construct()
        self._window.add_transient_window(ew)
        #self._window.set_message('Editor launched')

register_action(OpenEditorWindowAction)


class OpenConsoleWindowAction(Action):
    id = 'OpenConsoleWindow'
    label = _('_Console')
    tooltip = 'Open the Gaphor Console'

    def init(self, window):
        self._window = window

    def execute(self):
        from gaphor.ui.consolewindow import ConsoleWindow
        
        ew = ConsoleWindow()
        ew.construct()
        self._window.add_transient_window(ew)
        #self._window.set_message('Console launched')

register_action(OpenConsoleWindowAction)

class ManualAction(Action):
    id = 'Manual'
    label = _('_Manual')
    stock_id = 'gtk-help'
    tooltip='Manual for Gaphor'

    def init(self, window):
        self._window = window

    def execute(self):
        dialog = gtk.MessageDialog(self._window.get_window(),
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
            "For the manual, have a look at:\nhttp://gaphor.sourceforge.net/manual")
        dialog.run()
        dialog.destroy()


register_action(ManualAction)

class AboutAction(Action):
    id = 'About'
    label = _('_About')
    stock_id = 'gtk-about'
    tooltip='About Gaphor'
    
    def init(self, window):
        self._window = window

    def execute(self):
        data_dir =  os.path.join(pkg_resources.get_distribution('gaphor').location, 'gaphor', 'data')
        logo = gtk.gdk.pixbuf_new_from_file(os.path.join(data_dir, 'pixmaps', 'logo.png'))
        version = Application.distribution.version
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
        add_label('<span size="small">Copyright (c) 2001-2007 Arjan J. Molenaar</span>', 8, 8)
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
    label = _('_New diagram')
    stock_id = 'gaphor-diagram'

    element_factory = inject('element_factory')
    action_manager = inject('action_manager')

    def init(self, window):
        self._window = window

    def update(self):
        element = self._window.get_tree_view().get_selected_element()
        self.sensitive = isinstance(element, UML.Package)

    def execute(self):
        element = self._window.get_tree_view().get_selected_element()
        diagram = self.element_factory.create(UML.Diagram)
        diagram.package = element

        diagram.name = '%s diagram' % element.name

        self._window.select_element(diagram)
        self.action_manager.execute('OpenModelElement')
        self.action_manager.execute('RenameModelElement')

register_action(CreateDiagramAction, 'SelectRow')


class DeleteDiagramAction(Action):
    id = 'DeleteDiagram'
    label = _('_Delete diagram')
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
    label = _('_Open')

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
    label = _('_Rename')

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
    label = _('_Refresh')

    def init(self, window):
        self._window = window

    def execute(self):
        self._window.get_model().refresh()

register_action(RefreshNamespaceModelAction)


class DeleteCommand(Action):
    """Delete a model element through the tree view. This is only applicable
    to Diagram's and is not undoable."""
    id = 'DeleteElement'
    label = _('_Delete')

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

class UndoStackAction(Action):
    """
    Dummy action that triggers the undo and redo actions to update
    themselves.
    """
    id = 'UndoStack'
    
    def init(self, window):
        pass

register_action(UndoStackAction)

class UndoAction(Action):
    id = 'Undo'
    stock_id = 'gtk-undo'
    label = _('_Undo')
    tooltip = 'Undo the most recent changes'
    accel = 'C-z'

    # TODO: check if the diagram can undo.
    action_manager = inject('action_manager')

    def init(self, window):
        self._window = window

    def update(self):
        self.sensitive = get_undo_manager().can_undo()

    def execute(self):
        get_undo_manager().undo_transaction()
        self.update()
        self.action_manager.execute('UndoStack')

register_action(UndoAction, 'UndoStack')


class RedoAction(Action):
    id = 'Redo'
    stock_id = 'gtk-redo'
    tooltip = 'Redo the undone changes'
    accel = 'C-r'

    action_manager = inject('action_manager')

    def init(self, window):
        self._window = window

    def update(self):
        self.sensitive = get_undo_manager().can_redo()

    def execute(self):
        get_undo_manager().redo_transaction()
        #self.update()
        self.action_manager.execute('UndoStack')

register_action(RedoAction, 'UndoStack')


class RecentFileAction(ObjectAction):
    """Objects created by the RecentFilesSlot are of this kind.
    """

    action_manager = inject('action_manager')

    def init(self, window, filename):
        self._window = window
        self._filename = filename

    def update(self):
        pass

    def execute(self):
        revert_action = self.action_manager.get_action('FileRevert')
        revert_action.load(self._filename)


class RecentFilesSlot(DynamicMenu):
    """This is the dynamic menu that contains a list of recently opened
    model files.
    """

    gui_manager = inject('gui_manager')
    properties = inject('properties')
    action_manager = inject('action_manager')

    def __init__(self, slot_id):
        DynamicMenu.__init__(self, slot_id)

    def get_menu(self):
        recent_files = self.properties('recent-files', [])
        window = self.gui_manager.main_window
        file_list = []
        for f, i in zip(recent_files, xrange(len(recent_files))):
            id = 'RecentFile_%d' % i
            try:
                action = self.action_manager.get_action(id)
                action._label='_%d. %s' % (i+1, f)
                action._tooltip='Load %s.' % f
            except ActionError:
                # Create a new one if the is none registered
                action = RecentFileAction(id,
                                          label='_%d. %s' % (i+1, f),
                                          tooltip='Load %s.' % f)
                self.action_manager.set_action(action)
            action.init(window, f)
            file_list.append(id)
        return file_list

register_slot('RecentFiles', RecentFilesSlot)

# vim: sw=4:et
