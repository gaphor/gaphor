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
from gaphor.misc.errorhandler import error_handler, ErrorHandlerAspect, weave_method
DEFAULT_EXT='.gaphor'

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
          <toolitem action="file-open" />
          <separator />
          <toolitem action="file-save" />
          <toolitem action="file-save-as" />
          <separator />
        </toolbar>
      </ui>
    """

    def __init__(self):
        self._filename = None

    def init(self, app):
        self._app = app
        self.action_group = build_action_group(self)
        for name, label in (('file-recent-files', '_Recent files'),):
            a = gtk.Action(name, label, None, None)
            a.set_property('hide-if-empty', False)
            self.action_group.add_action(a)

        #recent_files = self.properties('recent-files', [])
        for i in xrange(0, 9):
            a = gtk.Action('file-recent-%d' % i, None, None, None)
            a.set_property('visible', False)
            self.action_group.add_action(a)
            a.connect('activate', self.load_recent, i)
        self.update_recent_files()

    def shutdown(self):
        pass

    def _set_filename(self, filename):
        if filename != self._filename:
            self._filename = filename
            self.update_recent_files(filename)

    filename = property(lambda s: s._filename, _set_filename)

    def update_recent_files(self, new_filename=None):
        recent_files = self.properties.get('recent-files', []) 
        if new_filename and new_filename not in recent_files:
            recent_files.insert(0, new_filename)
            recent_files = recent_files[0:9]
            self.properties.set('recent-files', recent_files)

        for i in xrange(0, 9):
            self.action_group.get_action('file-recent-%d' % i).set_property('visible', False)

        for i, f in enumerate(recent_files):
            id = 'file-recent%d' % i
            a = self.action_group.get_action('file-recent-%d' % i)
            a.props.label = '_%d. %s' % (i+1, f.replace('_', '__'))
            a.props.tooltip = 'Load %s.' % f
            a.props.visible = True

    def load_recent(self, action, index):
        recent_files = self.properties.get('recent-files', []) 
        filename = recent_files[index]
        self._load(filename)
        component.handle(FileManagerStateChanged(self))
        
    @action(name='file-new', stock_id='gtk-new')
    def new(self):
        element_factory = self.element_factory
        main_window = self.gui_manager.main_window
        if element_factory.size():
            dialog = gtk.MessageDialog(main_window.window,
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
        diagram.name= _('main')
        self.filename = None
        element_factory.notify_model()

        main_window.select_element(diagram)
        main_window.show_diagram(diagram)

        component.handle(FileManagerStateChanged(self))


    def _load(self, filename):
        try:
            from gaphor import storage
            log.debug('Loading from: %s' % filename)
            main_window = self.gui_manager.main_window
            queue = Queue()
            win = show_status_window(_('Loading...'), _('Loading model from %s') % filename, main_window.window, queue)
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

            # Let this be handled by the main window itself:
            #self._window.set_message('Model loaded successfully')
            view = main_window.tree_view

            self.filename = filename

            # Expand all root elements:
            view.expand_root_nodes()
        finally:
            try:
                win.destroy()
            except:
                pass


    def _save(self, filename):
        if filename and len(filename) > 0:
            from gaphor import storage
            if not filename.endswith(DEFAULT_EXT):
                filename = filename + DEFAULT_EXT

            queue = Queue()
            log.debug('Saving to: %s' % filename)
            win = show_status_window('Saving...', 'Saving model to %s' % filename, self.gui_manager.main_window.window, queue)
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
                win.destroy()

    @action(name='file-open', stock_id='gtk-open')
    def _open_dialog(self, title):
        filesel = gtk.FileChooserDialog(title=title,
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
        if not filename or response != gtk.RESPONSE_OK:
            return
        return filename


    @action(name='file-new-template', label=_('New from template'))
    def new_from_template(self):
        filename = self._open_dialog('New Gaphor model from template')
        if filename:
            self._load(filename)

            # It's a template: unset filename
            self.filename = None
            component.handle(FileManagerStateChanged(self))


    @action(name='file-open', stock_id='gtk-open')
    def open(self):
        filename = self._open_dialog('Open Gaphor model')
        if filename:
            self._load(filename)
            component.handle(FileManagerStateChanged(self))


    @action(name='file-save', stock_id='gtk-save')
    def save(self):
        filename = self.filename
        if filename:
            self._save(filename)
            component.handle(FileManagerStateChanged(self))
        else:
            self.save_as()


    @action(name='file-save-as', stock_id='gtk-save-as')
    def save_as(self):
        filename = self.filename
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
        self._save(filename)
        component.handle(FileManagerStateChanged(self))


def show_status_window(title, message, parent=None, queue=None):
    """
    Create a borderless window on the parent (main window), with a label and
    a progress bar.
    """
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title(title)
    win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
    win.set_transient_for(parent)
    win.set_modal(True)
    win.set_resizable(False)
    win.set_decorated(False)
    win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_SPLASHSCREEN)
    frame = gtk.Frame()
    win.add(frame)
    frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    vbox = gtk.VBox(spacing=12)
    frame.add(vbox)
    vbox.set_border_width(12)
    label = gtk.Label(message)
    label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
    vbox.pack_start(label)
    progress_bar = gtk.ProgressBar()
    progress_bar.set_size_request(400, -1)
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

# vim:sw=4:et:ai
