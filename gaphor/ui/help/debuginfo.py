import datetime
import logging
import sys
import textwrap
import time
from types import TracebackType

import better_exceptions

from gaphor.event import Notification
from gaphor.i18n import gettext
from gaphor.ui.selftest import system_information

logger = logging.getLogger(__name__)

better_exceptions.SUPPORTS_COLOR = False

START_TIME = time.time()


class DebugInfo:
    def __init__(self, application):
        self.application = application
        self.exceptions: list[
            tuple[float, type[BaseException], BaseException, TracebackType | None]
        ] = []
        self._orig_excepthook = sys.excepthook
        sys.excepthook = self.excepthook

    def shutdown(self):
        sys.excepthook = self._orig_excepthook

    def create_debug_info(self):
        buffer = []

        buffer.append(system_information())
        buffer.append("\n\n")

        if not self.exceptions:
            buffer.append(gettext("No errors have been intercepted. We’re good."))
            return "".join(buffer)

        buffer.append(gettext("Errors:"))
        buffer.append("\n\n")

        def print_exception(tp, v, tb, depth=0):
            for line in better_exceptions.format_exception(tp, v, tb):
                buffer.append(textwrap.indent(line, "  " * depth + "|"))
            if issubclass(tp, BaseExceptionGroup):
                for i, sub_exc in enumerate(v.exceptions):
                    buffer.append(
                        f"{'  ' * depth}{'└─┬──' if i == 0 else '  ├──'}────────────────────────────╌┄┈\n"
                    )
                    print_exception(
                        type(sub_exc), sub_exc, sub_exc.__traceback__, depth=depth + 1
                    )
                buffer.append(
                    f"{'  ' * (depth + 1)}└─────────────────────────────╌┄┈\n"
                )
            elif depth == 0:
                buffer.append("└─────────────────────────────╌┄┈\n")

        for ts, tp, v, tb in self.exceptions:
            buffer.append(
                f"Time since application startup: {datetime.timedelta(seconds=int(ts - START_TIME))}\n"
            )
            print_exception(tp, v, tb)

            return "".join(buffer)

    def excepthook(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
        self.exceptions.append((time.time(), exc_type, exc_value, exc_traceback))
        logger.exception(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        if session := self.application.active_session:
            session.get_service("event_manager").handle(
                Notification(
                    gettext(
                        "An unexpected error occurred.\nPlease file an issue on GitHub and include information from About Gaphor → Troubleshooting → Debugging Information."
                    )
                )
            )
