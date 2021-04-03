import logging
import os.path

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.ui.filedialog import open_file_dialog

log = logging.getLogger(__name__)


FILTERS = [
    (gettext("All Gaphor Models"), "*.gaphor", "application/x-gaphor"),
]


class AppFileManager(Service, ActionProvider):
    """Handle application level file loading."""

    def __init__(self, application, session):
        self.application = application
        self.session = session
        self.last_dir = None

    def shutdown(self):
        pass

    def load(self, filename):
        reuse_session = self.session_is_new(self.application.active_session)
        if reuse_session:
            session = self.application.active_session
            file_manager = session.get_service("file_manager")
            file_manager.load(filename)
        else:
            session = self.application.new_session(filename=filename)

    def new(self):
        self.application.new_session()

    def session_is_new(self, session):
        """If it's a new model, there is no state change (undo & redo) and no
        file name is defined."""
        if not session:
            return False

        undo_manager = session.get_service("undo_manager")
        file_manager = session.get_service("file_manager")

        return (
            not undo_manager.can_undo()
            and not undo_manager.can_redo()
            and not file_manager.filename
        )

    @property
    def main_window(self):
        return self.session.get_service("main_window")

    @action(name="app.file-new", shortcut="<Primary>n")
    def action_new(self):
        """The new model menu action.

        This action will create a new UML model.  This will trigger a
        FileManagerStateChange event.
        """

        self.new()

    @action(name="app.file-new-template")
    def action_new_from_template(self):
        """This menu action opens the new model from template dialog."""

        filenames = open_file_dialog(
            gettext("New Gaphor Model From Template"),
            parent=self.main_window.window,
            filters=FILTERS,
        )
        for filename in filenames:
            self.load(filename)
            self.filename = None
            self.last_dir = os.path.dirname(filename)

    @action(name="app.file-open", shortcut="<Primary>o")
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        filenames = open_file_dialog(
            gettext("Open Gaphor Model"),
            parent=self.main_window.window,
            dirname=self.last_dir,
            filters=FILTERS,
        )

        for filename in filenames:
            self.load(filename)
            self.last_dir = os.path.dirname(filename)

    @action(name="app.file-open-recent")
    def action_open_recent(self, filename: str):
        self.load(filename)
