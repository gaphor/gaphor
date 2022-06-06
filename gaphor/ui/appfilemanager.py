import logging
import os.path

from gi.repository import Gtk

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
    def parent_window(self):
        return (
            self.application.active_session.get_service("main_window").window
            if self.application.active_session
            else None
        )

    @action(name="app.file-open", shortcut="<Primary>o")
    def action_open(self):
        """This menu action opens the standard model open dialog."""

        def open_files(filenames):
            for filename in filenames:
                if self.application.has_session(filename):
                    dialog = Gtk.MessageDialog(
                        message_type=Gtk.MessageType.QUESTION,
                        buttons=Gtk.ButtonsType.YES_NO,
                        text=gettext(
                            "{filename} is already opened. Do you want to switch to the opened window instead?"
                        ).format(filename=filename),
                    )
                    dialog.set_transient_for(self.parent_window)

                    def response(dialog, answer):
                        force_new_session = answer != Gtk.ResponseType.YES
                        dialog.destroy()
                        self.application.new_session(
                            filename=filename, force=force_new_session
                        )

                    dialog.connect("response", response)
                    dialog.set_modal(True)
                    dialog.show()
                else:
                    self.application.new_session(filename=filename)

                self.last_dir = os.path.dirname(filename)

        open_file_dialog(
            gettext("Open a Model"),
            open_files,
            parent=self.parent_window,
            dirname=self.last_dir,
            filters=FILTERS,
        )
