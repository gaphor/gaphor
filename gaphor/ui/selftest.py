import logging
import sys
import time

import cairo
import gi
from gi.repository import GLib, Gtk, Pango

from gaphor.abc import Service
from gaphor.application import Application, distribution

log = logging.getLogger(__name__)


class Status:
    def __init__(self, name):
        self.name = name
        self.status = "in progress"

    def complete(self):
        self.status = "complete"

    @property
    def completed(self):
        return self.status == "complete"

    def __repr__(self):
        return f"{self.name}: {self.status}"


def test(func):
    """A test function."""

    def wrapper(self):
        status = Status(func.__name__)
        self.statuses.append(status)
        return func(self, status)

    return wrapper


class SelfTest(Service):
    def __init__(self, application: Application):
        self.application = application
        self.statuses: list[Status] = []

    def shutdown(self):
        pass

    def init(self, gtk_app):
        windows_console_output_workaround()
        self.init_timer(gtk_app, timeout=20)
        self.test_library_versions()
        self.test_new_session()

    def init_timer(self, gtk_app, timeout):
        start = time.time()

        def callback():
            if all(status.completed for status in self.statuses):
                log.info(
                    "All tests have been completed in %.1fs %s",
                    time.time() - start,
                    self.statuses,
                )
                gtk_app.quit()
                return GLib.SOURCE_REMOVE
            elif time.time() > start + timeout:
                log.error("Not all tests have passed: %s", self.statuses)
                gtk_app.exit_code = 1
                gtk_app.quit()
                return GLib.SOURCE_REMOVE
            return GLib.SOURCE_CONTINUE

        GLib.timeout_add(priority=GLib.PRIORITY_LOW, interval=100, function=callback)

    @test
    def test_library_versions(self, status):
        log.info("Gaphor version:    %s", distribution().version)
        log.info("Python version:    %s", sys.version)
        log.info(
            "GTK version:       %d.%d.%d",
            Gtk.get_major_version(),
            Gtk.get_minor_version(),
            Gtk.get_micro_version(),
        )
        log.info("PyGObject version: %d.%d.%d", *gi.version_info)
        log.info("Pycairo version:   %s", cairo.version)
        log.info("Cairo version:     %s", cairo.cairo_version_string())
        log.info("Pango version:     %s", Pango.version_string())
        status.complete()

    @test
    def test_new_session(self, status):
        session = self.application.new_session()

        def check_new_session(session):
            main_window = session.get_service("main_window")

            if main_window.window and main_window.window.get_visible():
                status.complete()
                return GLib.SOURCE_REMOVE
            else:
                return GLib.SOURCE_CONTINUE

        GLib.idle_add(check_new_session, session, priority=GLib.PRIORITY_LOW)


def windows_console_output_workaround():
    if sys.platform == "win32":
        from gaphor.ui import LOG_FORMAT

        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            filename="gaphor-self-test.txt",
            filemode="w",
            force=True,
        )
