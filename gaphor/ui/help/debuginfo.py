import datetime
import logging
import sys
import time
import traceback
from types import TracebackType

from gaphor.event import Notification
from gaphor.i18n import gettext
from gaphor.ui.selftest import system_information

logger = logging.getLogger(__name__)

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

        for ts, tp, v, tb in self.exceptions:
            buffer.append(
                f"Time since application startup: {datetime.timedelta(seconds=int(ts - START_TIME))}\n"
            )
            buffer.extend(
                traceback.TracebackException(tp, v, tb, capture_locals=True).format()
            )

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
