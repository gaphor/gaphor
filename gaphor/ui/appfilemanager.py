import logging

from gi.repository import Gio

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.ui.filedialog import FileDialog
from gaphor.ui.questiondialog import QuestionDialog

log = logging.getLogger(__name__)


FILTERS = [
    {"name": gettext("Gaphor Models"), "pattern": "*.gaphor"},
    {"name": gettext("All Files"), "pattern": "*"},
]


class AppFileManager(Service, ActionProvider):
    """
    Handle application level file loading
    """

    def __init__(self, session):
        self.session = session

    def shutdown(self):
        pass

    @property
    def application(self):
        return Gio.Application.get_default()

    def load(self, filename):
        if self.active_session_is_new():
            file_manager = self.session.get_service("file_manager")
            file_manager.load(filename)
        else:
            self.application.open([Gio.File.new_for_path(filename)], "")

    def new(self):
        self.application.open([], "__new__")

    def active_session_is_new(self):
        """
        If it's a new model, there is no state change (undo & redo)
        and no file name is defined.
        """
        undo_manager = self.session.get_service("undo_manager")
        file_manager = self.session.get_service("file_manager")

        return (
            not undo_manager.can_undo()
            and not undo_manager.can_redo()
            and not file_manager.filename
        )

    @property
    def main_window(self):
        return self.session.get_service("main_window")

    def file_dialog(self, title):
        file_dialog = FileDialog(title, filters=FILTERS, parent=self.main_window.window)

        filename = file_dialog.selection

        file_dialog.destroy()

        log.debug(filename)

        return filename

    @action(name="app.file-new", shortcut="<Primary>n")
    def action_new(self):
        """The new model menu action.  This action will create a new
        UML model.  This will trigger a FileManagerStateChange event."""

        self.new()

    @action(name="app.file-new-template")
    def action_new_from_template(self):
        """This menu action opens the new model from template dialog."""

        filename = self.file_dialog(gettext("New Gaphor Model From Template"))
        if filename:
            self.load(filename)
            self.filename = None

    @action(name="app.file-open", shortcut="<Primary>o")
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        filename = self.file_dialog(gettext("Open Gaphor Model"))

        if filename:
            self.load(filename)

    @action(name="app.file-open-recent")
    def action_open_recent(self, filename: str):
        self.load(filename)
