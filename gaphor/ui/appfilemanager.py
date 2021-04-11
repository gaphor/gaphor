import logging
import os.path

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.ui.filedialog import open_file_dialog
from gaphor.ui.questiondialog import QuestionDialog

log = logging.getLogger(__name__)


FILTERS = [
    (gettext("All Gaphor Models"), "*.gaphor", "application/x-gaphor"),
]


class AppFileManager(Service, ActionProvider):
    """Handle application level file loading."""

    def __init__(self, application):
        self.application = application
        self.last_dir = None

    def shutdown(self):
        pass

    @property
    def main_window(self):
        return self.application.active_session.get_service("main_window")

    @action(name="app.file-new", shortcut="<Primary>n")
    def action_new(self):
        """The new model menu action.

        This action will create a new UML model.  This will trigger a
        FileManagerStateChange event.
        """
        self.application.new_session()

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
            force_new_session = False
            if self.application.has_session(filename):
                dialog = QuestionDialog(
                    gettext(
                        "{filename} is already opened. Do you want to switch to the opened window instead?"
                    ).format(filename=filename),
                    parent=self.main_window.window,
                )

                force_new_session = not dialog.answer
                dialog.destroy()

            self.application.new_session(filename=filename, force=force_new_session)
            self.last_dir = os.path.dirname(filename)

    @action(name="app.file-open-recent")
    def action_open_recent(self, filename: str):
        self.application.new_session(filename=filename)
