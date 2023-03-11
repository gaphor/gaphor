"""The file service is responsible for loading and saving the user data."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Callable

from gaphas.decorators import g_async
from gi.repository import Adw, Gtk

from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler, gettext
from gaphor.core.modeling import Diagram, StyleSheet
from gaphor.event import (
    ModelLoaded,
    ModelSaved,
    SessionCreated,
    SessionShutdown,
    SessionShutdownRequested,
)
from gaphor.storage import storage
from gaphor.storage.mergeconflict import split_ours_and_theirs
from gaphor.storage.parser import MergeConflictDetected
from gaphor.ui.errorhandler import error_handler
from gaphor.ui.filedialog import GAPHOR_FILTER, save_file_dialog
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
        diagram = element_factory.create(Diagram)
        diagram.element = model
        diagram.name = gettext("New diagram")
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
        self._filename: Path | None = None

        event_manager.subscribe(self._on_session_shutdown_request)
        event_manager.subscribe(self._on_session_created)

    def shutdown(self):
        """Called when shutting down the file manager service."""
        self.event_manager.unsubscribe(self._on_session_shutdown_request)
        self.event_manager.unsubscribe(self._on_session_created)

    @property
    def filename(self) -> Path | None:
        """Return the current file name.

        This method is used by the filename property.
        """
        return self._filename

    @filename.setter
    def filename(self, filename: Path | str | None):
        """Sets the current file name.

        This method is used by the filename property.
        """

        if filename != self._filename:
            self._filename = Path(filename) if filename else None

    def load_template(self, template):
        storage.load(template, self.element_factory, self.modeling_language)
        self.event_manager.handle(ModelLoaded(self))

    def load(self, filename: Path, on_load_done: Callable[[], None] | None = None):
        """Load the Gaphor model from the supplied file name.

        A status window displays the loading progress. The load
        generator updates the progress queue.  The loader is passed to a
        GIdleThread which executes the load generator. If loading is
        successful, the filename is set.
        """
        # First claim file name, so any other files will be opened in a different session
        self.filename = filename

        status_window = StatusWindow(
            gettext("Loading…"),
            gettext("Loading model from {filename}").format(filename=filename),
            parent=self.parent_window,
        )

        def done():
            status_window.destroy()
            if on_load_done:
                on_load_done()
            else:
                self.event_manager.handle(ModelLoaded(self, filename))

        for _ in self._load_async(filename, status_window.progress, done):
            pass

    @g_async()
    def _load_async(
        self, filename: Path, progress: Callable[[int], None] | None = None, done=None
    ):
        try:
            with open(filename, encoding="utf-8", errors="replace") as file_obj:
                for percentage in storage.load_generator(
                    file_obj,
                    self.element_factory,
                    self.modeling_language,
                ):
                    if progress:
                        progress(percentage)
                    yield percentage
        except MergeConflictDetected:
            self.filename = None
            self.resolve_merge_conflict(filename)
        except Exception:
            self.filename = None
            error_handler(
                message=gettext("Unable to open model “{filename}”.").format(
                    filename=filename.name
                ),
                secondary_message=gettext(
                    "This file does not contain a valid Gaphor model."
                ),
                window=self.parent_window,
                close=lambda: self.event_manager.handle(SessionShutdown(self)),
            )
        finally:
            if done:
                done()

    def resolve_merge_conflict(self, filename: Path):
        temp_dir = tempfile.TemporaryDirectory()
        current_filename = Path(temp_dir.name) / f"current-{filename.name}"
        incoming_filename = Path(temp_dir.name) / f"incoming-{filename.name}"
        with (
            current_filename.open("wb") as current_file,
            incoming_filename.open("wb") as incoming_file,
        ):
            split = split_ours_and_theirs(filename, current_file, incoming_file)

        def done():
            nonlocal temp_dir
            temp_dir.cleanup()
            self.filename = filename
            self.event_manager.handle(ModelLoaded(self, filename, modified=True))

        def handle_merge_conflict(answer):
            if answer == "cancel":
                self.event_manager.handle(SessionShutdown(self))
            elif answer == "current":
                self.load(current_filename, on_load_done=done)
            elif answer == "incoming":
                self.load(incoming_filename, on_load_done=done)
            else:
                raise ValueError(f"Unknown resolution for merge conflict: {answer}")

        if split:
            resolve_merge_conflict_dialog(
                self.parent_window, filename, handle_merge_conflict
            )
        else:
            error_handler(
                message=gettext("Unable to open model “{filename}”.").format(
                    filename=filename.name
                ),
                secondary_message=gettext(
                    "This file does not contain a valid Gaphor model."
                ),
                window=self.parent_window,
                close=lambda: self.event_manager.handle(SessionShutdown(self)),
            )

    def save(self, filename, on_save_done=None):
        """Save the current UML model to the specified file name.

        Before writing the model file, this will verify that there are
        no orphan references.  It will also verify that the filename has
        the correct extension.  A status window is displayed while the
        GIdleThread is executed.  This thread actually saves the model.
        """

        if not filename or (filename.exists() and not filename.is_file()):
            return

        status_window = StatusWindow(
            gettext("Saving…"),
            gettext("Saving model to {filename}").format(filename=filename),
            parent=self.parent_window,
        )

        @g_async()
        def async_saver():
            try:
                with filename.open("w", encoding="utf-8") as out:
                    for percentage in storage.save_generator(out, self.element_factory):
                        status_window.progress(percentage)
                        yield

                self.filename = filename
                self.event_manager.handle(ModelSaved(self, filename))
            except Exception as e:
                error_handler(
                    message=gettext("Unable to save model “{filename}”.").format(
                        filename=filename
                    ),
                    secondary_message=error_message(e),
                    window=self.parent_window,
                )
                raise
            finally:
                status_window.destroy()
            if on_save_done:
                on_save_done()

        for _ in async_saver():
            pass

    @property
    def parent_window(self):
        return self.main_window.window if self.main_window else None

    @action(name="file-save", shortcut="<Primary>s")
    def action_save(self):
        """Save the file. Depending on if there is a file name, either perform
        the save directly or present the user with a save dialog box.

        Returns True if the saving actually succeeded.
        """

        if filename := self.filename:
            self.save(filename)
        else:
            self.action_save_as()

    @action(name="file-save-as", shortcut="<Primary><Shift>s")
    def action_save_as(self):
        """Save the model in the element_factory by allowing the user to select
        a file name."""

        return save_file_dialog(
            gettext("Save Gaphor Model As"),
            self.save,
            parent=self.parent_window,
            filename=self.filename,
            extension=".gaphor",
            filters=GAPHOR_FILTER,
        )

    @event_handler(SessionCreated)
    def _on_session_created(self, event: SessionCreated) -> None:
        if event.filename:
            self.load(event.filename)
        elif event.template:
            self.load_template(event.template)
        else:
            load_default_model(self.element_factory)

    @event_handler(SessionShutdownRequested)
    def _on_session_shutdown_request(self, event: SessionShutdownRequested) -> None:
        """Ask user to close window if the model has changed.

        The user is asked to either discard the changes, keep the
        application running or save the model and quit afterwards.
        """

        def confirm_shutdown():
            self.event_manager.handle(SessionShutdown(self))

        def response(answer):
            if answer == "save":
                if filename := self.filename:
                    self.save(filename, on_save_done=confirm_shutdown)

                else:
                    save_file_dialog(
                        gettext("Save Gaphor Model As"),
                        lambda filename: self.save(
                            filename, on_save_done=confirm_shutdown
                        ),
                        parent=self.parent_window,
                        filename=self.filename,
                        extension=".gaphor",
                        filters=GAPHOR_FILTER,
                    )
            elif answer == "discard":
                confirm_shutdown()

        if self.main_window.model_changed:
            save_changes_before_closing_dialog(self.parent_window, response)
        else:
            confirm_shutdown()


def resolve_merge_conflict_dialog(window: Gtk.Window, filename: Path, handler) -> None:
    dialog = Adw.MessageDialog.new(
        window,
        gettext("Resolve Merge Conflict?"),
    )
    dialog.set_body(
        gettext(
            "The model you are opening contains a merge conflict. Do you want to open the current model or the incoming change to the model?"
        )
    )
    dialog.add_response("cancel", gettext("Cancel"))
    dialog.add_response("current", gettext("Open Current"))
    dialog.add_response("incoming", gettext("Open Incoming"))
    dialog.set_close_response("cancel")

    def response(dialog, answer):
        dialog.set_transient_for(None)
        dialog.destroy()
        handler(answer)

    dialog.connect("response", response)
    dialog.show()


def save_changes_before_closing_dialog(window: Gtk.Window, handler) -> None:
    title = gettext("Save Changes?")
    body = gettext(
        "The open model contains unsaved changes. Changes which are not saved will be permanently lost."
    )
    dialog = Adw.MessageDialog.new(
        window,
        title,
    )
    dialog.set_body(body)
    dialog.add_response("cancel", gettext("Cancel"))
    dialog.add_response("discard", gettext("Discard"))
    dialog.add_response("save", gettext("Save"))
    dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
    dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
    dialog.set_default_response("save")
    dialog.set_close_response("cancel")

    def response(dialog, answer):
        # Unset transient window: it can cause crashes on flatpak
        # when all windows are destroyed at once.
        dialog.set_transient_for(None)
        dialog.destroy()
        handler(answer)

    dialog.connect("response", response)
    dialog.show()
