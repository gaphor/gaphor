"""The file service is responsible for loading and saving the user data."""

import logging
from queue import Queue

from gaphas.decorators import g_async
from gi.repository import GLib, Gtk

from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler, gettext
from gaphor.core.modeling.stylesheet import StyleSheet
from gaphor.event import (
    ModelLoaded,
    ModelSaved,
    SessionCreated,
    SessionShutdown,
    SessionShutdownRequested,
)
from gaphor.storage import storage, verify
from gaphor.storage.xmlwriter import XMLWriter
from gaphor.ui.errorhandler import error_handler
from gaphor.ui.filedialog import GAPHOR_FILTER, save_file_dialog
from gaphor.ui.questiondialog import QuestionDialog
from gaphor.ui.statuswindow import StatusWindow

DEFAULT_EXT = ".gaphor"
MAX_RECENT = 10

log = logging.getLogger(__name__)


def error_message(e):
    if not isinstance(e, IOError):
        return gettext(
            "Gaphor was not able to store the model, probably due to an internal error:\n{exc}\nIf you think this is a bug, please contact the developers."
        ).format(exc=str(e))
    if e.errno == 13:
        return gettext(
            "You do not have the permissions necessary to save the model.\nPlease check that you typed the location correctly and try again."
        )
    elif e.errno == 28:
        return gettext(
            "You do not have enough free space on the device to save the model.\nPlease free up some disk space and try again or save it in a different location."
        )
    return gettext(
        "The model cannot be stored at this location:\n{exc}\nPlease check that you typed the location correctly and try again."
    ).format(exc=str(e))


def load_default_model(element_factory):
    element_factory.flush()
    with element_factory.block_events():
        element_factory.create(StyleSheet)
        model = element_factory.create(UML.Package)
        model.name = gettext("New model")
        diagram = element_factory.create(UML.Diagram)
        diagram.package = model
        diagram.name = gettext("main")
    element_factory.model_ready()


class FileManager(Service, ActionProvider):
    """The file service, responsible for loading and saving Gaphor models."""

    def __init__(self, event_manager, element_factory, modeling_language, main_window):
        """File manager constructor.

        There is no current filename yet.
        """
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        self.main_window = main_window
        self._filename = None

        event_manager.subscribe(self._on_session_shutdown_request)
        event_manager.subscribe(self._on_session_created)

    def shutdown(self):
        """Called when shutting down the file manager service."""
        self.event_manager.unsubscribe(self._on_session_shutdown_request)
        self.event_manager.unsubscribe(self._on_session_created)

    def get_filename(self):
        """Return the current file name.

        This method is used by the filename property.
        """
        return self._filename

    def set_filename(self, filename):
        """Sets the current file name.

        This method is used by the filename property. Setting the
        current filename will update the recent file list.
        """

        if filename != self._filename:
            self._filename = filename

    filename = property(get_filename, set_filename)

    def load(self, filename):
        """Load the Gaphor model from the supplied file name.

        A status window displays the loading progress.  The load
        generator updates the progress queue.  The loader is passed to a
        GIdleThread which executes the load generator.  If loading is
        successful, the filename is set.
        """
        # First claim file name, so any other files will be opened in a different session
        self.filename = filename
        queue: Queue[int] = Queue(0)
        status_window = StatusWindow(
            gettext("Loading..."),
            gettext("Loading model from {filename}").format(filename=filename),
            parent=self.main_window.window,
            queue=queue,
        )

        # Use low prio, so screen updates do happen
        @g_async(priority=GLib.PRIORITY_DEFAULT_IDLE)
        def async_loader():
            try:
                for percentage in storage.load_generator(
                    filename.encode("utf-8"),
                    self.element_factory,
                    self.modeling_language,
                ):
                    queue.put(percentage)
                    yield percentage

                self.event_manager.handle(ModelLoaded(self, filename))
            except Exception:
                self.filename = None
                error_handler(
                    message=gettext("Unable to open model “{filename}”.").format(
                        filename=filename
                    ),
                    secondary_message=gettext(
                        "This file does not contain a valid Gaphor model."
                    ),
                    window=self.main_window.window,
                )
                load_default_model(self.element_factory)
                raise
            finally:
                status_window.destroy()

        for _ in async_loader():
            pass

    def verify_orphans(self):
        """Verify that no orphaned elements are saved.

        This method checks of there are any orphan references in the
        element factory.  If orphans are found, a dialog is displayed
        asking the user if it is OK to unlink them.
        """

        orphans = verify.orphan_references(self.element_factory)

        if orphans:
            log.info("Found orphan references %s", orphans)
            main_window = self.main_window

            dialog = QuestionDialog(
                gettext(
                    "The model contains some references to items that are not maintained. Do you want to clean the model before saving?"
                ),
                parent=main_window.window,
            )

            answer = dialog.answer
            dialog.destroy()

            if not answer:
                for orphan in orphans:
                    orphan.unlink()

    def save(self, filename):
        """Save the current UML model to the specified file name.

        Before writing the model file, this will verify that there are
        no orphan references.  It will also verify that the filename has
        the correct extension.  A status window is displayed while the
        GIdleThread is executed.  This thread actually saves the model.
        """

        if not (filename and len(filename)):
            return

        self.verify_orphans()

        main_window = self.main_window
        queue: Queue[int] = Queue(0)
        status_window = StatusWindow(
            gettext("Saving..."),
            gettext("Saving model to {filename}").format(filename=filename),
            parent=main_window.window,
            queue=queue,
        )

        @g_async(priority=GLib.PRIORITY_DEFAULT_IDLE)
        def async_saver():
            try:
                with open(filename.encode("utf-8"), "w") as out:
                    for percentage in storage.save_generator(
                        XMLWriter(out), self.element_factory
                    ):
                        queue.put(percentage)
                        yield

                self.filename = filename
                self.event_manager.handle(ModelSaved(self, filename))
            except Exception as e:
                error_handler(
                    message=gettext("Unable to save model “{filename}”.").format(
                        filename=filename
                    ),
                    secondary_message=error_message(e),
                    window=self.main_window.window,
                )
                raise
            finally:
                status_window.destroy()

        for _ in async_saver():
            pass

    @action(name="file-save", shortcut="<Primary>s")
    def action_save(self):
        """Save the file. Depending on if there is a file name, either perform
        the save directly or present the user with a save dialog box.

        Returns True if the saving actually succeeded.
        """

        filename = self.filename

        if not filename:
            return self.action_save_as()

        self.save(filename)
        return True

    @action(name="file-save-as", shortcut="<Primary><Shift>s")
    def action_save_as(self):
        """Save the model in the element_factory by allowing the user to select
        a file name.

        Returns True if the saving actually happened.
        """

        filename = save_file_dialog(
            gettext("Save Gaphor Model As"),
            parent=self.main_window.window,
            filename=self.filename,
            extension=".gaphor",
            filters=GAPHOR_FILTER,
        )

        if filename:
            self.save(filename)
            return True

        return False

    @event_handler(SessionCreated)
    def _on_session_created(self, event: SessionCreated):
        if event.filename:
            self.load(event.filename)
        else:
            load_default_model(self.element_factory)

    @event_handler(SessionShutdownRequested)
    def _on_session_shutdown_request(self, event):
        """Ask user to close window if the model has changed.

        The user is asked to either discard the changes, keep the
        application running or save the model and quit afterwards.
        """

        def confirm_shutdown():
            self.event_manager.handle(SessionShutdown(self))

        if self.main_window.model_changed:
            response = save_changes_before_closing_dialog(self.main_window.window)
            if response == Gtk.ResponseType.YES:
                saved = self.action_save()
                if saved:
                    confirm_shutdown()
            if response == Gtk.ResponseType.REJECT:
                confirm_shutdown()
        else:
            confirm_shutdown()


def save_changes_before_closing_dialog(window):
    dialog = Gtk.MessageDialog(
        window,
        Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
        Gtk.MessageType.WARNING,
    )
    dialog.props.text = gettext("Save changed to your model before closing?")
    dialog.props.secondary_text = gettext(
        "If you close without saving, your changes will be discarded."
    )

    dialog.add_buttons(
        gettext("Close _without saving"),
        Gtk.ResponseType.REJECT,
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_SAVE,
        Gtk.ResponseType.YES,
    )
    dialog.set_default_response(Gtk.ResponseType.YES)
    response = dialog.run()
    dialog.destroy()

    return response
