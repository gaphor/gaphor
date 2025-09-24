"""The file service is responsible for loading and saving the user data."""

from __future__ import annotations

import logging
import tempfile
from collections.abc import Awaitable, Callable
from functools import partial
from pathlib import Path

from gi.repository import Adw, Gio, Gtk

import gaphor.storage as storage
from gaphor.abc import ActionProvider, Service
from gaphor.babel import translate_model
from gaphor.core import action, event_handler, gettext
from gaphor.core.changeset.compare import compare
from gaphor.core.modeling import ElementFactory, ModelReady
from gaphor.event import (
    ModelSaved,
    Notification,
    SessionCreated,
    SessionShutdown,
    SessionShutdownRequested,
)
from gaphor.storage.mergeconflict import split_ours_and_theirs
from gaphor.storage.parser import MergeConflictDetected
from gaphor.ui.errordialog import error_dialog
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


class FileManager(Service, ActionProvider):
    """The file service, responsible for loading and saving Gaphor models."""

    def __init__(self, event_manager, element_factory, modeling_language, main_window):
        """File manager constructor.

        There is no current filename yet.
        """
        super().__init__()
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        self.main_window = main_window
        self._filename: Path | None = None
        self._monitor: Gio.Monitor | None = None

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
        translated_model = translate_model(template)
        storage.load(translated_model, self.element_factory, self.modeling_language)
        self.event_manager.handle(ModelReady(self))

    async def load(self, filename: Path):
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

        try:
            await self._load_async(filename, status_window.progress)
        finally:
            status_window.done()
        self.event_manager.handle(ModelReady(self, filename=filename))

    @action("file-reload")
    async def reload(self):
        if self.filename and self.filename.exists():
            self.element_factory.flush()

            await self.load(self.filename)
            self.event_manager.handle(ModelReady(self))

    async def merge(
        self,
        ancestor_filename: Path,
        current_filename: Path,
        incoming_filename: Path,
    ):
        status_window = StatusWindow(
            gettext("Loading…"),
            gettext("Loading current and incoming model"),
            parent=self.parent_window,
        )

        async def progress(percentage, completed=0):
            await status_window.progress(completed + percentage / 3)

        try:
            log.debug("Loading current model from %s", current_filename)
            await self._load_async(current_filename, progress)

            log.debug("Loading ancestor model from %s", ancestor_filename)
            ancestor_element_factory = ElementFactory()
            await self._load_async(
                ancestor_filename,
                partial(progress, completed=33),
                element_factory=ancestor_element_factory,
            )

            log.debug("Loading incoming model from %s", incoming_filename)
            incoming_element_factory = ElementFactory()
            await self._load_async(
                incoming_filename,
                partial(progress, completed=66),
                element_factory=incoming_element_factory,
            )

            log.debug("Comparing models")
            with self.element_factory.block_events():
                list(
                    compare(
                        self.element_factory,
                        ancestor_element_factory,
                        incoming_element_factory,
                    )
                )
        finally:
            status_window.done()

    async def _load_async(
        self,
        filename: Path,
        progress: Callable[[float], Awaitable[None]] | None = None,
        element_factory=None,
    ):
        factory = element_factory or self.element_factory
        try:
            with filename.open(encoding="utf-8", errors="replace") as file_obj:
                for percentage in storage.load_generator(
                    file_obj,
                    factory,
                    self.modeling_language,
                ):
                    if progress:
                        await progress(percentage)
        except MergeConflictDetected:
            self.filename = None
            await self.resolve_merge_conflict(filename)
        except Exception:
            self.filename = None
            await error_dialog(
                message=gettext("Unable to open model “{filename}”.").format(
                    filename=filename
                ),
                secondary_message=gettext(
                    "This file does not contain a valid Gaphor model."
                ),
                window=self.parent_window,
            )
            self.event_manager.handle(SessionShutdown(quitting=False))

    async def resolve_merge_conflict(self, filename: Path):
        temp_dir = tempfile.TemporaryDirectory()
        ancestor_filename = Path(temp_dir.name) / f"ancestor-{filename.name}"
        current_filename = Path(temp_dir.name) / f"current-{filename.name}"
        incoming_filename = Path(temp_dir.name) / f"incoming-{filename.name}"
        with (
            ancestor_filename.open("wb") as ancestor_file,
            current_filename.open("wb") as current_file,
            incoming_filename.open("wb") as incoming_file,
        ):
            split = split_ours_and_theirs(
                filename, ancestor_file, current_file, incoming_file
            )

        if split:
            answer = await resolve_merge_conflict_dialog(self.parent_window)
            if answer == "cancel":
                self.event_manager.handle(SessionShutdown(quitting=False))
            elif answer == "current":
                await self.load(current_filename)
            elif answer == "incoming":
                await self.load(incoming_filename)
            elif answer == "manual":
                await self.merge(ancestor_filename, current_filename, incoming_filename)
            else:
                raise ValueError(f"Unknown resolution for merge conflict: {answer}")

            temp_dir.cleanup()
            self.filename = filename
            self.event_manager.handle(
                ModelReady(self, filename=filename, modified=True)
            )
        else:
            await error_dialog(
                message=gettext("Unable to open model “{filename}”.").format(
                    filename=filename.name
                ),
                secondary_message=gettext(
                    "This file does not contain a valid Gaphor model."
                ),
                window=self.parent_window,
            )
            self.event_manager.handle(SessionShutdown(quitting=False))

    async def save(self, filename):
        """Save the current model to the specified file name.

        Before writing the model file, this will verify that there are
        no orphan references. It will also verify that the filename has
        the correct extension. A status window is displayed while the
        save operation is executed.
        """

        if not filename or (filename.exists() and not filename.is_file()):
            return

        status_window = (
            StatusWindow(
                gettext("Saving…"),
                gettext("Saving model to {filename}").format(filename=filename),
                parent=self.parent_window,
            )
            if self.element_factory.size() > 100
            else None
        )

        try:
            with filename.open("w", encoding="utf-8") as out:
                for percentage in storage.save_generator(out, self.element_factory):
                    if status_window:
                        await status_window.progress(percentage)
            self.event_manager.handle(ModelSaved(filename))
        except Exception as e:
            await error_dialog(
                message=gettext("Unable to save model “{filename}”.").format(
                    filename=filename
                ),
                secondary_message=error_message(e),
                window=self.parent_window,
            )
            raise
        else:
            self.filename = filename
        finally:
            if status_window:
                status_window.done()
            self.event_manager.handle(Notification(gettext("Model has been saved.")))

    @property
    def parent_window(self):
        return self.main_window.window if self.main_window else None

    @action(name="file-save", shortcut="<Primary>s")
    async def action_save(self):
        """Save the file. Depending on if there is a file name, either perform
        the save directly or present the user with a save dialog box.

        Returns True if the saving actually succeeded.
        """

        if filename := self.filename:
            await self.save(filename)
        else:
            await self._save_as()

    @action(name="file-save-as", shortcut="<Primary><Shift>s")
    async def action_save_as(self):
        """Save the model in the element_factory by allowing the user to select
        a file name."""
        await self._save_as()

    async def _save_as(self):
        filename = await save_file_dialog(
            gettext("Save Gaphor Model As"),
            self.filename or Path(gettext("New Model")).with_suffix(DEFAULT_EXT),
            parent=self.parent_window,
            filters=GAPHOR_FILTER,
        )
        await self.save(filename)

    @event_handler(SessionCreated)
    async def _on_session_created(self, event: SessionCreated) -> None:
        if event.filename:
            await self.load(event.filename)
            self.event_manager.handle(ModelReady(self))
        elif event.template:
            self.load_template(event.template)
        else:
            self.event_manager.handle(ModelReady(self, filename=event.filename))

    @event_handler(SessionShutdownRequested)
    async def _on_session_shutdown_request(
        self, event: SessionShutdownRequested
    ) -> None:
        """Ask user to close window if the model has changed.

        The user is asked to either discard the changes, keep the
        application running or save the model and quit afterwards.
        """

        def confirm_shutdown():
            self.event_manager.handle(SessionShutdown(quitting=event.quitting))

        if self.main_window.model_changed:
            answer = await save_changes_before_close_dialog(self.parent_window)
            if answer == "save":
                if filename := self.filename:
                    await self.save(filename)
                    confirm_shutdown()
                else:
                    filename = await save_file_dialog(
                        gettext("Save Gaphor Model As"),
                        self.filename
                        or Path(gettext("New Model")).with_suffix(DEFAULT_EXT),
                        parent=self.parent_window,
                        filters=GAPHOR_FILTER,
                    )
                    if filename:
                        await self.save(filename)
                        confirm_shutdown()
            elif answer == "discard":
                confirm_shutdown()
        else:
            confirm_shutdown()


async def resolve_merge_conflict_dialog(window: Gtk.Window) -> str:
    dialog = Adw.AlertDialog.new(
        gettext("Resolve Merge Conflict?"),
        gettext(
            "The model you are opening contains a merge conflict. Do you want to open the current model or the incoming change to the model?"
        ),
    )
    dialog.add_response("cancel", gettext("Cancel"))
    dialog.add_response("manual", gettext("Open Merge Editor"))
    dialog.add_response("current", gettext("Open Current"))
    dialog.add_response("incoming", gettext("Open Incoming"))
    dialog.set_close_response("cancel")

    return str(await dialog.choose(window))


async def save_changes_before_close_dialog(window: Gtk.Window) -> str:
    title = gettext("Save Changes?")
    body = gettext(
        "The open model contains unsaved changes. Changes which are not saved will be permanently lost."
    )
    dialog = Adw.AlertDialog.new(title, body)
    dialog.add_response("cancel", gettext("Cancel"))
    dialog.add_response("discard", gettext("Discard"))
    dialog.add_response("save", gettext("Save"))
    dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
    dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
    dialog.set_default_response("save")
    dialog.set_close_response("cancel")

    window.present()

    return str(await dialog.choose(window))
