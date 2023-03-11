import logging
import os.path

from gi.repository import Adw

from pathlib import Path

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.ui.filedialog import open_file_dialog

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
    def window(self):
        return self.application.active_window

    @action(name="app.file-open")
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        def open_files(filenames):
            for filename in filenames:
                if self.application.has_session(filename):
                    name = Path(filename).name
                    title = gettext("Switch to {name}?").format(name=name)
                    body = gettext(
                        "{name} is already opened. Do you want to switch to the opened window instead?"
                    ).format(name=name)
                    dialog = Adw.MessageDialog.new(
                        self.window,
                        title,
                    )
                    dialog.set_body(body)
                    dialog.add_response("open", gettext("Open Again"))
                    dialog.add_response("switch", gettext("Switch"))
                    dialog.set_response_appearance(
                        "switch", Adw.ResponseAppearance.SUGGESTED
                    )
                    dialog.set_default_response("switch")
                    dialog.set_close_response("open")

                    def response(dialog, answer):
                        dialog.destroy()
                        self.application.new_session(
                            filename=filename, force=(answer == "open")
                        )

                    dialog.connect("response", response)
                    dialog.show()
                else:
                    self.application.new_session(filename=filename)

                self.last_dir = os.path.dirname(filename)

        open_file_dialog(
            gettext("Open a Model"),
            open_files,
            parent=self.window,
            dirname=self.last_dir,
            filters=FILTERS,
        )
