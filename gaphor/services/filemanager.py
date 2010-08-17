"""
The file service is responsible for loading and saving the user data.
"""

import gc
import gobject, pango, gtk
from zope import interface, component
from gaphor.interfaces import IService, IActionProvider, IServiceEvent
from gaphor.core import _, inject, action, build_action_group
from gaphor import UML
from gaphor.misc.gidlethread import GIdleThread, Queue, QueueEmpty
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.misc.errorhandler import error_handler
from gaphor.ui.statuswindow import StatusWindow
from gaphor.ui.questiondialog import QuestionDialog

DEFAULT_EXT = '.gaphor'
MAX_RECENT = 10

class FileManagerStateChanged(object):
    """
    Event class used to send state changes on the ndo Manager.
    """

    interface.implements(IServiceEvent)

    def __init__(self, service):
        self.service = service


class FileManager(object):
    """
    The file service, responsible for loading and saving Gaphor models.
    """

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')
    gui_manager = inject('gui_manager')
    properties = inject('properties')

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="file">
            <placeholder name="primary">
              <menuitem action="file-new" />
              <menuitem action="file-new-template" />
              <menuitem action="file-open" />
              <menu name="recent" action="file-recent-files">
                <menuitem action="file-recent-0" />
                <menuitem action="file-recent-1" />
                <menuitem action="file-recent-2" />
                <menuitem action="file-recent-3" />
                <menuitem action="file-recent-4" />
                <menuitem action="file-recent-5" />
                <menuitem action="file-recent-6" />
                <menuitem action="file-recent-7" />
                <menuitem action="file-recent-8" />
              </menu>
              <separator />
              <menuitem action="file-save" />
              <menuitem action="file-save-as" />
              <separator />
            </placeholder>
          </menu>
        </menubar>
        <toolbar action="mainwindow-toolbar">
          <placeholder name="left">
            <toolitem action="file-open" />
            <separator />
            <toolitem action="file-save" />
            <toolitem action="file-save-as" />
            <separator />
          </placeholder>
        </toolbar>
      </ui>
    """

    def __init__(self):
        """File manager constructor.  There is no current filename yet."""

        self._filename = None

    def init(self, app):
        """File manager service initialization.  The app parameter
        is the main application object.  This method builds the
        action group in the file menu.  The list of recent
        Gaphor files is then updated in the file menu."""
    
        self._app = app
        self.action_group = build_action_group(self)

        for name, label in (('file-recent-files', '_Recent files'),):
            action = gtk.Action(name, label, None, None)
            action.set_property('hide-if-empty', False)
            self.action_group.add_action(action)

        for i in xrange(0, (MAX_RECENT-1)):
            action = gtk.Action('file-recent-%d' % i, None, None, None)
            action.set_property('visible', False)
            self.action_group.add_action(action)
            action.connect('activate', self.load_recent, i)
            
        self.update_recent_files()

    def shutdown(self):
        """Called when shutting down the file manager service."""

        log.info('Shutting down file manager service')
        
    def get_filename(self):
        """Return the current file name.  This method is used by the filename
        property."""
        return self._filename

    def set_filename(self, filename):
        """Sets the current file name.  This method is used by the filename
        property.  Setting the current filename will update the recent file
        list."""

        log.info('Setting current file')
        log.debug(filename)

        if filename != self._filename:
            self._filename = filename
            self.update_recent_files(filename)

    filename = property(get_filename, set_filename)
    
    def get_recent_files(self):
        """Returns the recent file list from the properties service.  This
        method is used by the recent_files property."""
        
        return self.properties.get('recent-files', [])
        
    def set_recent_files(self, recent_files):
        """Updates the properties service with the supplied list of recent 
        files.  This method is used by the recent_files property."""
        
        self.properties.set('recent-files', recent_files)
        
    recent_files = property(get_recent_files, set_recent_files)

    def update_recent_files(self, new_filename=None):
        """Updates the list of recent files.  If the new_filename
        parameter is supplied, it is added to the list of recent files.
        
        The default recent file placeholder actions are hidden.  The real
        actions are then built using the recent file list."""

        recent_files = self.recent_files
        
        if new_filename and new_filename not in recent_files:
            recent_files.insert(0, new_filename)
            recent_files = recent_files[0:(MAX_RECENT-1)]
            self.recent_files = recent_files

        for i in xrange(0, (MAX_RECENT-1)):
            action = self.action_group.get_action('file-recent-%d' % i)
            action.set_property('visible', False)

        for i, filename in enumerate(recent_files):
            id = 'file-recent%d' % i
            action = self.action_group.get_action('file-recent-%d' % i)
            action.props.label = '_%d. %s' % (i+1, filename.replace('_', '__'))
            action.props.tooltip = 'Load %s.' % filename
            action.props.visible = True

    def load_recent(self, action, index):
        """Load the recent file at the specified index.  This will trigger
        a FileManagerStateChanged event.  The recent files are stored in
        the recent_files property."""

        filename = self.recent_files[index]

        self.load(filename)
        self._app.handle(FileManagerStateChanged(self))
        
    def load(self, filename):
        """Load the specified filename."""

        try:
            from gaphor.storage import storage
            log.debug('Loading from: %s' % filename)
            main_window = self.gui_manager.main_window
            queue = Queue()
            status_window = StatusWindow(_('Loading...'),\
                                         _('Loading model from %s') % filename,\
                                         parent=main_window.window,\
                                         queue=queue)
            gc.collect()
            worker = GIdleThread(storage.load_generator(filename, self.element_factory), queue)
            #self._window.action_pool.insensivate_actions()
            #undo_manager.clear_undo_stack()
            #get_undo_manager().clear_redo_stack()
            worker.start()
            worker.wait()
            if worker.error:
                log.error('Error while loading model from file %s: %s' % (filename, worker.error))
                error_handler(message='Error while loading model from file %s' % filename, exc_info=worker.exc_info)

            self.filename = filename

        finally:
            try:
                status_window.destroy()
            except:
                pass


    def _save(self, filename):
        """Save the current UML model to the specified file name."""

        if filename and len(filename) > 0:
            from gaphor.storage import verify
            orphans = verify.orphan_references(self.element_factory)
            if orphans:
                main_window = self.gui_manager.main_window

                dialog = QuestionDialog(_("The model contains some references"\
                                          " to items that are not maintained."\
                                          " Do you want to clean this before"\
                                          " saving the model?"),\
                                        parent=main_window.window)
              
                answer = dialog.answer
                dialog.destroy()
                
                if not answer:
                    for o in orphans:
                        o.unlink()
                    assert not verify.orphan_references(self.element_factory)

            from gaphor.storage import storage
            if not filename.endswith(DEFAULT_EXT):
                filename = filename + DEFAULT_EXT

            main_window = self.gui_manager.main_window
            queue = Queue()
            log.debug('Saving to: %s' % filename)
            status_window = StatusWindow('Saving...',\
                                         'Saving model to %s' % filename,\
                                         parent=main_window.window,\
                                         queue=queue)
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

                self.filename = filename

                # Restore states of actions
                #self._window.action_pool.set_action_states(action_states)
            finally:
                status_window.destroy()

    def _open_dialog(self, title):
        """Open a file chooser dialog to select a model
        file to open."""

        filesel = gtk.FileChooserDialog(title=title,
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        filesel.set_transient_for(self.gui_manager.main_window.window)

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
        if not filename or response != gtk.RESPONSE_OK:
            return
        return filename

    @action(name='file-new', stock_id='gtk-new')
    def action_new(self):
        """The new model menu action.  This action will create a new
        UML model.  This will trigger a FileManagerStateChange event."""

        log.info('New model')

        element_factory = self.element_factory
        main_window = self.gui_manager.main_window
        if element_factory.size():
            dialog = QuestionDialog(_("Opening a new model will flush the"\
                                      " currently loaded model.\nAny changes"\
                                      " made will not be saved. Do you want to"\
                                      " continue?"),\
                                    parent=main_window.window)
           
            answer = dialog.answer
            dialog.destroy()
            
            if not answer:
                return

        element_factory.flush()
        gc.collect()
        model = element_factory.create(UML.Package)
        model.name = _('New model')
        diagram = element_factory.create(UML.Diagram)
        diagram.package = model
        diagram.name= _('main')
        self.filename = None
        element_factory.notify_model()

        #main_window.select_element(diagram)
        #main_window.show_diagram(diagram)

        self._app.handle(FileManagerStateChanged(self))

    @action(name='file-new-template', label=_('New from template'))
    def action_new_from_template(self):
        """This menu action opens the new model from template dialog."""

        log.info('Creating from template')

        filename = self._open_dialog('New Gaphor model from template')

        log.debug(filename)

        if filename:
            self.load(filename)

            # It's a template: unset filename
            self.filename = None
            self._app.handle(FileManagerStateChanged(self))


    @action(name='file-open', stock_id='gtk-open')
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        log.info('Opening file')

        filename = self._open_dialog('Open Gaphor model')

        log.debug(filename)

        if filename:
            self.load(filename)
            self._app.handle(FileManagerStateChanged(self))


    @action(name='file-save', stock_id='gtk-save')
    def action_save(self):
        """
        Save the file. Depending on if there is a file name, either perform
        the save directly or present the user with a save dialog box.

        Returns True if the saving actually succeeded.
        """

        log.info('Saving file')

        filename = self.filename

        log.debug(filename)

        if filename:
            self._save(filename)
            self._app.handle(FileManagerStateChanged(self))
            return True
        else:
            return self.action_save_as()


    @action(name='file-save-as', stock_id='gtk-save-as')
    def action_save_as(self):
        """
        Save the model in the element_factory by allowing the
        user to select a file name.

        Returns True if the saving actually happened.
        """
    
        log.info('Saving file')

        filename = self.filename

        log.debug(filename)

        filesel = gtk.FileChooserDialog(title=_('Save Gaphor model as'),
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_SAVE,
                                                 gtk.RESPONSE_OK))
        filesel.set_transient_for(self.gui_manager.main_window.window)

        if filename:
            filesel.set_current_name(filename)
        try:
            response = filesel.run()
            filename = None
            filesel.hide()
            if response == gtk.RESPONSE_OK:
                filename = filesel.get_filename()
                if filename:
                    self._save(filename)
                    self._app.handle(FileManagerStateChanged(self))
                    return True
        finally:
            filesel.destroy()
        return False

# vim:sw=4:et:ai
