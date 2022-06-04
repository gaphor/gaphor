from __future__ import annotations

import logging
import sys
import time
from types import TracebackType

import stackprinter
from gi.repository import Gtk

from gaphor.abc import ActionProvider
from gaphor.action import action
from gaphor.event import Notification
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui.abc import UIComponent

_EXCEPTHOOK = sys.excepthook

log = logging.getLogger(__name__)

START_TIME = time.time()


def new_builder():
    builder = Gtk.Builder()
    ui_file = (
        "errorreports.glade" if Gtk.get_major_version() == 3 else "errorreports.ui"
    )
    builder.add_from_string(
        translated_ui_string("gaphor.plugins.errorreports", ui_file)
    )
    return builder


class ErrorReports(UIComponent, ActionProvider):
    def __init__(self, event_manager, main_window, tools_menu):
        self.event_manager = event_manager
        self.main_window = main_window
        tools_menu.add_actions(self)
        self.window = None
        self.buffer = None
        self.exceptions: list[
            tuple[float, type[BaseException], BaseException, TracebackType | None]
        ] = []
        sys.excepthook = self.excepthook

    def shutdown(self):
        super().shutdown()
        sys.excepthook = _EXCEPTHOOK

    @action(name="error-reports-open", label=gettext("Error Reports"))
    def open(self):
        if self.window:
            self.window.set_property("has-focus", True)
            return

        builder = new_builder()

        self.window = builder.get_object("error-reports")
        self.buffer = builder.get_object("buffer")

        self.window.set_transient_for(self.main_window.window)
        self.window.show_all()
        self.window.connect("destroy", self.close)

        self.update_text()

    def close(self, widget=None):
        if self.window:
            self.window.destroy()
            self.window = None
            self.buffer = None

    def update_text(self):
        buffer = self.buffer
        if not buffer:
            return

        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())

        if not self.exceptions:
            buffer.insert(
                buffer.get_end_iter(),
                "No errors have been intercepted. We’re good.",
            )
            return

        for ts, tp, v, tb in self.exceptions:
            buffer.insert(
                buffer.get_end_iter(), f"At time delta {ts - START_TIME:.2f}:\n"
            )
            buffer.insert(
                buffer.get_end_iter(), stackprinter.format((tp, v, tb), line_wrap=0)
            )
            buffer.insert(buffer.get_end_iter(), "\n===\n")

    def excepthook(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
        self.exceptions.append((time.time(), exc_type, exc_value, exc_traceback))
        log.exception(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        self.update_text()
        self.event_manager.handle(
            Notification(
                gettext(
                    "An unexpected error occurred.\nPlease file an issue on GitHub and include information from Tools → Error Reports."
                )
            )
        )
