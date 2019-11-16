"""
The file service is responsible for loading and saving the user data.
"""

import logging
import urllib.parse
from typing import Optional

from gi.repository import Gtk

import gaphor.ui
from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler, translate
from gaphor.misc.errorhandler import error_handler
from gaphor.misc.gidlethread import GIdleThread, Queue, QueueEmpty, QueueFull
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.storage import storage, verify
from gaphor.ui.event import FileLoaded, FileSaved, WindowClosed
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

    def __init__(self, event_manager, element_factory, main_window, properties):
        """File manager constructor.  There is no current filename yet."""
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.main_window = main_window
        self.properties = properties
        self._filename = None

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
        property. Setting the current filename will update the recent file
        list."""

        if filename != self._filename:
            self._filename = filename

    filename = property(get_filename, set_filename)

    def load(self, filename):
        """Load the Gaphor model from the supplied file name.  A status window
        displays the loading progress.  The load generator updates the progress
        queue.  The loader is passed to a GIdleThread which executes the load
        generator.  If loading is successful, the filename is set."""

        queue = Queue()
        status_window: Optional[StatusWindow]
        main_window = self.main_window
        status_window = StatusWindow(
            translate("Loading..."),
            translate(f"Loading model from {filename}"),
            parent=main_window.window,
            queue=queue,
        )

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
            self.event_manager.handle(FileLoaded(self, filename))
        except (QueueEmpty, QueueFull):
            error_handler(
                message=translate("Error while loading model from file %s") % filename
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
                translate(
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
            translate("Saving..."),
            translate("Saving model to %s") % filename,
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
            self.event_manager.handle(FileSaved(self, filename))
        except (OSError, QueueEmpty, QueueFull):
            error_handler(
                message=translate("Error while saving model to file %s") % filename
            )
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

    @action(name="file-new", shortcut="<Primary>n")
    def action_new(self):
        """The new model menu action.  This action will create a new
        UML model.  This will trigger a FileManagerStateChange event."""

        element_factory = self.element_factory
        main_window = self.main_window

        if element_factory.size():
            dialog = QuestionDialog(
                translate(
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
            model.name = translate("New model")
            diagram = element_factory.create(UML.Diagram)
            diagram.package = model
            diagram.name = translate("main")
        self.filename = None
        element_factory.model_ready()

        # main_window.select_element(diagram)
        # main_window.show_diagram(diagram)

    @action(name="file-new-template")
    def action_new_from_template(self):
        """This menu action opens the new model from template dialog."""

        filters = [
            {"name": translate("Gaphor Models"), "pattern": "*.gaphor"},
            {"name": translate("All Files"), "pattern": "*"},
        ]

        file_dialog = FileDialog(
            translate("New Gaphor Model From Template"), filters=filters
        )

        filename = file_dialog.selection

        file_dialog.destroy()

        log.debug(filename)

        if filename:
            self.load(filename)
            self.filename = None

    @action(name="file-open", shortcut="<Primary>o")
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        filters = [
            {"name": translate("Gaphor Models"), "pattern": "*.gaphor"},
            {"name": translate("All Files"), "pattern": "*"},
        ]

        file_dialog = FileDialog(translate("Open Gaphor Model"), filters=filters)

        filename = file_dialog.selection

        file_dialog.destroy()

        log.debug(filename)

        if filename:
            self.load(filename)

    @action(name="file-open-recent")
    def action_open_recent(self, file_url: str):
        parsed_url = urllib.parse.urlparse(file_url)
        path = parsed_url.path
        self.load(path)

    @action(name="file-save", shortcut="<Primary>s")
    def action_save(self):
        """
        Save the file. Depending on if there is a file name, either perform
        the save directly or present the user with a save dialog box.

        Returns True if the saving actually succeeded.
        """

        filename = self.filename

        if filename:
            self.save(filename)
            return True
        else:
            return self.action_save_as()

    @action(name="file-save-as", shortcut="<Primary><Shift>s")
    def action_save_as(self):
        """
        Save the model in the element_factory by allowing the
        user to select a file name.

        Returns True if the saving actually happened.
        """

        file_dialog = FileDialog(
            translate("Save Gaphor Model As"), action="save", filename=self.filename
        )

        filename = file_dialog.selection

        file_dialog.destroy()

        if filename:
            self.save(filename)
            return True

        return False

    @action(name="app.quit", shortcut="<Primary>q")
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
                translate("Save changed to your model before closing?"),
            )
            dialog.format_secondary_text(
                translate(
                    "If you close without saving, your changes will be discarded."
                )
            )
            dialog.add_buttons(
                translate("Close _without saving"),
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
                    gaphor.ui.quit()
            if response == Gtk.ResponseType.REJECT:
                gaphor.ui.quit()
        else:
            gaphor.ui.quit()

    @event_handler(WindowClosed)
    def _on_window_close(self, event):
        self.file_quit()
