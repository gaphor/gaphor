import logging

from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.ui.filedialog import FileDialog

log = logging.getLogger(__name__)


FILTERS = [
    {"name": gettext("Gaphor Models"), "pattern": "*.gaphor"},
    {"name": gettext("All Files"), "pattern": "*"},
]


def load_default_model(session):
    element_factory = session.get_service("element_factory")
    element_factory.flush()
    with element_factory.block_events():
        model = element_factory.create(UML.Package)
        model.name = gettext("New model")
        diagram = element_factory.create(UML.Diagram)
        diagram.package = model
        diagram.name = gettext("main")
    element_factory.model_ready()


class AppFileManager(Service, ActionProvider):
    """Handle application level file loading."""

    def __init__(self, application, session):
        self.application = application
        self.session = session

    def shutdown(self):
        pass

    def load(self, filename):
        if self.active_session_is_new():
            session = self.session
        else:
            session = self.application.new_session()

        file_manager = session.get_service("file_manager")
        try:
            file_manager.load(filename)
        except Exception:
            load_default_model(session)
            raise

    def new(self):
        session = self.application.new_session()
        load_default_model(session)

    def active_session_is_new(self):
        """If it's a new model, there is no state change (undo & redo) and no
        file name is defined."""
        if not self.application.active_session:
            return False

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
        """The new model menu action.

        This action will create a new UML model.  This will trigger a
        FileManagerStateChange event.
        """

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
