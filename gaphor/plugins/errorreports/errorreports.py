from __future__ import annotations

import datetime
import logging
import sys
import textwrap
import time
from types import TracebackType

import better_exceptions
from gi.repository import Gtk

from gaphor.abc import ActionProvider
from gaphor.action import action
from gaphor.core.eventmanager import event_handler
from gaphor.event import Notification, SessionCreated
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui.abc import UIComponent
from gaphor.ui.selftest import system_information

better_exceptions.SUPPORTS_COLOR = False

log = logging.getLogger(__name__)

START_TIME = time.time()


def new_builder():
    builder = Gtk.Builder()
    builder.add_from_string(
        translated_ui_string("gaphor.plugins.errorreports", "errorreports.ui")
    )
    return builder


class ErrorReports(UIComponent, ActionProvider):
    def __init__(self, application, event_manager):
        self.application = application
        self.event_manager = event_manager
        self.window = None
        self.buffer = None
        self.exceptions: list[
            tuple[float, type[BaseException], BaseException, TracebackType | None]
        ] = []
        self._orig_excepthook = sys.excepthook
        sys.excepthook = self.excepthook
        event_manager.subscribe(self.on_session_created)

    def shutdown(self):
        super().shutdown()
        sys.excepthook = self._orig_excepthook
        self.event_manager.unsubscribe(self.on_session_created)

    @event_handler(SessionCreated)
    def on_session_created(self, event):
        session = event.session
        tools_menu = session.get_service("tools_menu")
        tools_menu.add_actions(self, scope="app")

    @action(name="app.error-reports-open", label=gettext("Error Reports"))
    def open(self):
        if self.window:
            self.window.present()
            return

        builder = new_builder()

        self.window = builder.get_object("error-reports")
        self.buffer = builder.get_object("buffer")

        self.window.connect("close-request", self.close)
        self.window.present()

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

        buffer.insert(buffer.get_end_iter(), system_information())
        buffer.insert(buffer.get_end_iter(), "\n\n")

        if not self.exceptions:
            buffer.insert(
                buffer.get_end_iter(),
                gettext("No errors have been intercepted. We’re good."),
            )
            return

        buffer.insert(buffer.get_end_iter(), gettext("Errors:"))
        buffer.insert(buffer.get_end_iter(), "\n\n")

        def print_exception(tp, v, tb, depth=0):
            assert buffer
            for line in better_exceptions.format_exception(tp, v, tb):
                buffer.insert(
                    buffer.get_end_iter(), textwrap.indent(line, "  " * depth + "|")
                )
            if issubclass(tp, BaseExceptionGroup):
                for i, sub_exc in enumerate(v.exceptions):
                    buffer.insert(
                        buffer.get_end_iter(),
                        f"{'  ' * depth}{'└─┬──' if i == 0 else '  ├──'}────────────────────────────╌┄┈\n",
                    )
                    print_exception(
                        type(sub_exc), sub_exc, sub_exc.__traceback__, depth=depth + 1
                    )
                buffer.insert(
                    buffer.get_end_iter(),
                    f"{'  ' * (depth + 1)}└─────────────────────────────╌┄┈\n",
                )
            elif depth == 0:
                buffer.insert(
                    buffer.get_end_iter(),
                    "└─────────────────────────────╌┄┈\n",
                )

        for ts, tp, v, tb in self.exceptions:
            buffer.insert(
                buffer.get_end_iter(),
                f"Time since application startup: {datetime.timedelta(seconds=int(ts - START_TIME))}\n",
            )
            print_exception(tp, v, tb)

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
        if session := self.application.active_session:
            session.get_service("event_manager").handle(
                Notification(
                    gettext(
                        "An unexpected error occurred.\nPlease file an issue on GitHub and include information from Tools → Error Reports."
                    )
                )
            )
