import importlib.resources
import logging
import platform
import sys
import textwrap
import time
import tempfile

import cairo
import gi
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, GtkSource, Pango

from gaphor.abc import Service
from gaphor.application import Application, distribution
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram

try:
    import pygit2
except ImportError:
    pass


log = logging.getLogger(__name__)


class Status:
    def __init__(self, name):
        self.name = name
        self.status = "in progress"

    def complete(self):
        self.status = "completed"

    def skip(self):
        self.status = "skipped"

    @property
    def in_progress(self):
        return self.status == "in progress"

    @property
    def completed(self):
        return self.status in ("completed", "skipped")

    def __repr__(self):
        return f"{self.name}: {self.status}"


def test(func):
    """A test function."""

    def wrapper(self):
        status = Status(func.__name__)
        self.statuses.append(status)
        try:
            return func(self, status)
        except BaseException:
            log.exception("Test %s failed", func.__name__)
            status.status = "failed"

    return wrapper


class SelfTest(Service):
    def __init__(self, application: Application):
        self.application = application
        self.statuses: list[Status] = []

    def shutdown(self):
        pass

    def init(self, gtk_app):
        windows_console_output_workaround()
        self.init_timer(gtk_app, timeout=30)
        self.test_library_versions()
        self.test_gsettings_schemas()
        self.test_new_session()
        self.test_auto_layout()
        self.test_git_support()

    def init_timer(self, gtk_app, timeout):
        start = time.time()

        def callback():
            if time.time() > start + timeout:
                log.error("Tests timed out")
                gtk_app.exit_code = 1
            elif any(status.in_progress for status in self.statuses):
                return GLib.SOURCE_CONTINUE
            elif all(status.completed for status in self.statuses):
                log.info(
                    "All tests have been completed in %.1fs",
                    time.time() - start,
                )
            else:
                log.error("Not all tests have passed")
                gtk_app.exit_code = 1

            for status in self.statuses:
                log.info(status)

            gtk_app.quit()
            return GLib.SOURCE_REMOVE

        GLib.timeout_add(priority=GLib.PRIORITY_LOW, interval=100, function=callback)

    @test
    def test_library_versions(self, status):
        log.info(
            "System information:\n\n%s", textwrap.indent(system_information(), "\t")
        )
        status.complete()

    @test
    def test_new_session(self, status):
        with (importlib.resources.files("gaphor") / "templates" / "uml.gaphor").open(
            encoding="utf-8"
        ) as f:
            session = self.application.new_session(template=f)

        def check_new_session(session):
            main_window = session.get_service("main_window")

            if main_window.window and main_window.window.get_visible():
                status.complete()
                return GLib.SOURCE_REMOVE
            else:
                return GLib.SOURCE_CONTINUE

        GLib.idle_add(check_new_session, session, priority=GLib.PRIORITY_LOW)

    @test
    def test_gsettings_schemas(self, status):
        source = Gio.settings_schema_source_get_default()
        if source.lookup("org.gtk.gtk4.Settings.FileChooser", recursive=True):
            log.info(
                "Schemas found in data dirs: %s",
                ":".join(GLib.get_system_data_dirs()),
            )
            status.complete()
        else:
            log.error(
                "Could not find schemas in data dirs: %s",
                ":".join(GLib.get_system_data_dirs()),
            )
            log.info("Schemas found: %s %s", *source.list_schemas(True))

    @test
    def test_auto_layout(self, status):
        session = self.application.new_session()
        event_manager = session.get_service("event_manager")
        element_factory = session.get_service("element_factory")
        auto_layout = session.get_service("auto_layout")

        with Transaction(event_manager):
            diagram = element_factory.create(Diagram)

        auto_layout.layout(diagram)
        status.complete()

    @test
    def test_git_support(self, status):
        if "pygit2" not in globals():
            status.skip()
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            pygit2.init_repository(temp_dir)
        status.complete()


def system_information():
    return textwrap.dedent(
        f"""\
        Gaphor version:         {distribution().version}
        Operating System:       {platform.system()} ({platform.release()})
        Display:                {display_type()}
        Python version:         {platform.python_version()}
        GTK version:            {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}
        Adwaita version:        {Adw.get_major_version()}.{Adw.get_minor_version()}.{Adw.get_micro_version()}
        GtkSourceView version:  {gtk_source_view_version()}
        Cairo version:          {cairo.cairo_version_string()}
        Pango version:          {Pango.version_string()}
        PyGObject version:      {gi.__version__}
        Pycairo version:        {cairo.version}
        pygit2/libgit2 version: {"pygit2" in globals() and f"{pygit2.__version__}  / {pygit2.LIBGIT2_VERSION}" or "-NONE-"}
        """
    )


def display_type():
    dm = Gdk.DisplayManager.get()
    display = dm.get_default_display()
    return display.__class__.__name__ if display else "none"


def gtk_source_view_version():
    if hasattr(GtkSource, "get_major_version"):
        return f"{GtkSource.get_major_version()}.{GtkSource.get_minor_version()}.{GtkSource.get_micro_version()}"
    else:
        return "-"


def windows_console_output_workaround():
    if sys.platform == "win32":
        from gaphor.main import LOG_FORMAT

        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            filename="gaphor-self-test.txt",
            filemode="w",
            force=True,
            encoding="utf-8",
        )
