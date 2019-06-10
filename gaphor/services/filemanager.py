"""
The file service is responsible for loading and saving the user data.
"""

import logging

from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, action, build_action_group, event_handler
from gaphor.abc import Service, ActionProvider
from gaphor.misc.errorhandler import error_handler
from gaphor.misc.gidlethread import GIdleThread, Queue
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.storage import storage, verify
from gaphor.ui.event import FilenameChanged, WindowClose
from gaphor.ui.filedialog import FileDialog
from gaphor.ui.questiondialog import QuestionDialog
from gaphor.ui.statuswindow import StatusWindow

DEFAULT_EXT = ".gaphor"
MAX_RECENT = 10

log = logging.getLogger(__name__)


class FileManager(Service, ActionProvider):
    """
    The file service, responsible for loading and saving Gaphor models.
    """

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
            <menuitem action="file-quit" />
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

    def __init__(self, event_manager, element_factory, main_window, properties):
        """File manager constructor.  There is no current filename yet."""
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.main_window = main_window
        self.properties = properties
        self._filename = None
        self.action_group = build_action_group(self)

        for name, label in (("file-recent-files", "_Recent files"),):
            action = Gtk.Action.new(name, label, None, None)
            action.set_property("hide-if-empty", False)
            self.action_group.add_action(action)

        for i in range(0, (MAX_RECENT - 1)):
            action = Gtk.Action.new("file-recent-%d" % i, None, None, None)
            action.set_property("visible", False)
            self.action_group.add_action(action)
            action.connect("activate", self.load_recent, i)

        self.update_recent_files()

        event_manager.subscribe(self._on_window_close)

    def shutdown(self):
        """Called when shutting down the file manager service."""
        self.event_manager.unsubscribe(self._on_window_close)

    def get_filename(self):
        """Return the current file name.  This method is used by the filename
        property."""
        return self._filename

    def set_filename(self, filename):
        """Sets the current file name.  This method is used by the filename
        property.  Setting the current filename will update the recent file
        list."""

        if filename != self._filename:
            self._filename = filename
            self.update_recent_files(filename)

    filename = property(get_filename, set_filename)

    def get_recent_files(self):
        """Returns the recent file list from the properties service.  This
        method is used by the recent_files property."""
        return self.properties.get("recent-files", [])

    def set_recent_files(self, recent_files):
        """Updates the properties service with the supplied list of recent
        files.  This method is used by the recent_files property."""

        self.properties.set("recent-files", recent_files)

    recent_files = property(get_recent_files, set_recent_files)

    def update_recent_files(self, new_filename=None):
        """Updates the list of recent files.  If the new_filename
        parameter is supplied, it is added to the list of recent files.

        The default recent file placeholder actions are hidden.  The real
        actions are then built using the recent file list."""

        recent_files = self.recent_files

        if new_filename and new_filename not in recent_files:
            recent_files.insert(0, new_filename)
            recent_files = recent_files[0 : (MAX_RECENT - 1)]
            self.recent_files = recent_files

        for i in range(0, (MAX_RECENT - 1)):
            action = self.action_group.get_action("file-recent-%d" % i)
            action.set_property("visible", False)

        for i, filename in enumerate(recent_files):
            id = "file-recent%d" % i
            action = self.action_group.get_action("file-recent-%d" % i)
            action.props.label = "_%d. %s" % (i + 1, filename.replace("_", "__"))
            action.props.tooltip = "Load %s." % filename
            action.props.visible = True

    def load_recent(self, action, index):
        """Load the recent file at the specified index.  This will trigger
        a FilenameChanged event.  The recent files are stored in
        the recent_files property."""

        filename = self.recent_files[index]

        self.load(filename)
        self.event_manager.handle(FilenameChanged(self, filename))

    def load(self, filename):
        """Load the Gaphor model from the supplied file name.  A status window
        displays the loading progress.  The load generator updates the progress
        queue.  The loader is passed to a GIdleThread which executes the load
        generator.  If loading is successful, the filename is set."""

        queue = Queue()

        try:
            main_window = self.main_window
            status_window = StatusWindow(
                _("Loading..."),
                _("Loading model from %s") % filename,
                parent=main_window.window,
                queue=queue,
            )
        except:
            log.warning("Could not create status window, proceding without.")
            status_window = None

        try:
            loader = storage.load_generator(
                filename.encode("utf-8"), self.element_factory
            )
            worker = GIdleThread(loader, queue)

            worker.start()
            worker.wait()

            if worker.error:
                worker.reraise()

            self.filename = filename
        except:
            error_handler(
                message=_("Error while loading model from file %s") % filename
            )
            raise
        finally:
            if status_window is not None:
                status_window.destroy()

    def verify_orphans(self):
        """Verify that no orphaned elements are saved.  This method checks
        of there are any orphan references in the element factory.  If orphans
        are found, a dialog is displayed asking the user if it is OK to
        unlink them."""

        orphans = verify.orphan_references(self.element_factory)

        if orphans:
            main_window = self.main_window

            dialog = QuestionDialog(
                _(
                    "The model contains some references"
                    " to items that are not maintained."
                    " Do you want to clean this before"
                    " saving the model?"
                ),
                parent=main_window.window,
            )

            answer = dialog.answer
            dialog.destroy()

            if not answer:
                for orphan in orphans:
                    orphan.unlink()

    def verify_filename(self, filename):
        """Verify that the supplied filename is using the proper default
        extension.  If not, the extension is added to the filename
        and returned."""

        if not filename.endswith(DEFAULT_EXT):
            filename = filename + DEFAULT_EXT

        return filename

    def save(self, filename):
        """Save the current UML model to the specified file name.  Before
        writing the model file, this will verify that there are no orphan
        references.  It will also verify that the filename has the correct
        extension.  A status window is displayed while the GIdleThread
        is executed.  This thread actually saves the model."""

        if not filename or not len(filename):
            return

        self.verify_orphans()
        filename = self.verify_filename(filename)

        main_window = self.main_window
        queue = Queue()
        status_window = StatusWindow(
            _("Saving..."),
            _("Saving model to %s") % filename,
            parent=main_window.window,
            queue=queue,
        )
        try:
            with open(filename.encode("utf-8"), "w") as out:
                saver = storage.save_generator(XMLWriter(out), self.element_factory)
                worker = GIdleThread(saver, queue)
                worker.start()
                worker.wait()

            if worker.error:
                worker.reraise()

            self.filename = filename
        except:
            error_handler(message=_("Error while saving model to file %s") % filename)
            raise
        finally:
            status_window.destroy()

    def _open_dialog(self, title):
        """Open a file chooser dialog to select a model
        file to open."""

        filesel = Gtk.FileChooserDialog(
            title=title,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )
        filesel.set_transient_for(self.main_window.window)

        filter = Gtk.FileFilter()
        filter.set_name("Gaphor models")
        filter.add_pattern("*.gaphor")
        filesel.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        filesel.add_filter(filter)

        if self.filename:
            filesel.set_current_name(self.filename)

        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if not filename or response != Gtk.ResponseType.OK:
            return
        return filename

    @action(name="file-new", stock_id="gtk-new")
    def action_new(self):
        """The new model menu action.  This action will create a new
        UML model.  This will trigger a FileManagerStateChange event."""

        element_factory = self.element_factory
        main_window = self.main_window

        if element_factory.size():
            dialog = QuestionDialog(
                _(
                    "Opening a new model will flush the"
                    " currently loaded model.\nAny changes"
                    " made will not be saved. Do you want to"
                    " continue?"
                ),
                parent=main_window.window,
            )

            answer = dialog.answer
            dialog.destroy()

            if not answer:
                return

        element_factory.flush()
        with element_factory.block_events():
            model = element_factory.create(UML.Package)
            model.name = _("New model")
            diagram = element_factory.create(UML.Diagram)
            diagram.package = model
            diagram.name = _("main")
        self.filename = None
        element_factory.notify_model()

        # main_window.select_element(diagram)
        # main_window.show_diagram(diagram)

        self.event_manager.handle(FilenameChanged(self))

    @action(name="file-new-template", label=_("New from template"))
    def action_new_from_template(self):
        """This menu action opens the new model from template dialog."""

        filters = [
            {"name": _("Gaphor Models"), "pattern": "*.gaphor"},
            {"name": _("All Files"), "pattern": "*"},
        ]

        file_dialog = FileDialog(_("New Gaphor Model From Template"), filters=filters)

        filename = file_dialog.selection

        file_dialog.destroy()

        log.debug(filename)

        if filename:
            self.load(filename)
            self.filename = None
            self.event_manager.handle(FilenameChanged(self))

    @action(name="file-open", stock_id="gtk-open")
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        filters = [
            {"name": _("Gaphor Models"), "pattern": "*.gaphor"},
            {"name": _("All Files"), "pattern": "*"},
        ]

        file_dialog = FileDialog(_("Open Gaphor Model"), filters=filters)

        filename = file_dialog.selection

        file_dialog.destroy()

        log.debug(filename)

        if filename:
            self.load(filename)
            self.event_manager.handle(FilenameChanged(self, filename))

    @action(name="file-save", stock_id="gtk-save")
    def action_save(self):
        """
        Save the file. Depending on if there is a file name, either perform
        the save directly or present the user with a save dialog box.

        Returns True if the saving actually succeeded.
        """

        filename = self.filename

        if filename:
            self.save(filename)
            self.event_manager.handle(FilenameChanged(self, filename))
            return True
        else:
            return self.action_save_as()

    @action(name="file-save-as", stock_id="gtk-save-as")
    def action_save_as(self):
        """
        Save the model in the element_factory by allowing the
        user to select a file name.

        Returns True if the saving actually happened.
        """

        file_dialog = FileDialog(
            _("Save Gaphor Model As"), action="save", filename=self.filename
        )

        filename = file_dialog.selection

        file_dialog.destroy()

        if filename:
            self.save(filename)
            self.event_manager.handle(FilenameChanged(self, filename))
            return True

        return False

    @action(name="file-quit", stock_id="gtk-quit")
    def file_quit(self):
        """
        Ask user to close window if the model has changed.
        The user is asked to either discard the changes, keep the
        application running or save the model and quit afterwards.
        """
        if self.main_window.model_changed:
            dialog = Gtk.MessageDialog(
                self.main_window.window,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.NONE,
                _("Save changed to your model before closing?"),
            )
            dialog.format_secondary_text(
                _("If you close without saving, your changes will be discarded.")
            )
            dialog.add_buttons(
                _("Close _without saving"),
                Gtk.ResponseType.REJECT,
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.YES,
            )
            dialog.set_default_response(Gtk.ResponseType.YES)
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                saved = self.action_save()
                if saved:
                    self.main_window.quit()
            if response == Gtk.ResponseType.REJECT:
                self.main_window.quit()
        else:
            self.main_window.quit()

    @event_handler(WindowClose)
    def _on_window_close(self, event):
        self.file_quit()
