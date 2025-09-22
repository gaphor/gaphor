import importlib.resources
import logging
import platform
import sys
import textwrap
import time

import cairo
import gi
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, GtkSource, Pango

from gaphor.abc import Service
from gaphor.application import Application, distribution
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.ui import APPLICATION_ID

log = logging.getLogger(__name__)


class Status:
    def __init__(self, name):
        self.name = name
        self.status = "in progress"

    def passed(self):
        self.status = "passed"

    def failed(self):
        self.status = "failed"

    @property
    def in_progress(self):
        return self.status == "in progress"

    @property
    def completed(self):
        return self.status in ("passed", "failed")

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
            status.failed()

    return wrapper


class SelfTest(Service):
    def __init__(self, application: Application):
        self.application = application
        self.statuses: list[Status] = []

    def shutdown(self):
        pass

    def open(self):
        pass

    def init(self, gtk_app):
        windows_console_output_workaround()
        self.init_timer(gtk_app, timeout=30)
        self.test_library_versions()
        self.test_gsettings_schemas()
        self.test_new_session()
        self.test_auto_layout()

    def init_timer(self, gtk_app, timeout):
        start = time.time()

        def callback():
            if all(status.completed for status in self.statuses):
                log.info(
                    "All tests have been completed in %.1fs",
                    time.time() - start,
                )
            elif time.time() > start + timeout:
                log.error("Tests timed out")
            elif any(status.in_progress for status in self.statuses):
                return GLib.SOURCE_CONTINUE
            else:
                log.error("Not all tests have passed")

            for status in self.statuses:
                log.log(logging.INFO if status.completed else logging.ERROR, status)

            gtk_app.exit_code = (
                0 if all(status.status == "passed" for status in self.statuses) else 1
            )
            gtk_app.quit()
            return GLib.SOURCE_REMOVE

        GLib.timeout_add(
            priority=GLib.PRIORITY_DEFAULT, interval=100, function=callback
        )

    @test
    def test_library_versions(self, status: Status):
        log.info(
            "System information:\n\n%s", textwrap.indent(system_information(), "\t")
        )
        status.passed()

    @test
    def test_new_session(self, status: Status):
        template = importlib.resources.files("gaphor") / "templates" / "uml.gaphor"
        session = self.application.new_session(template=template)

        main_window = session.get_service("main_window")

        if main_window.window and main_window.window.get_visible():
            status.passed()
        else:
            status.failed()

    @test
    def test_gsettings_schemas(self, status: Status):
        source = Gio.settings_schema_source_get_default()
        data_dirs = [GLib.get_user_data_dir(), *GLib.get_system_data_dirs()]
        for schema in ["org.gtk.gtk4.Settings.FileChooser", APPLICATION_ID]:
            if source.lookup(schema, recursive=True):
                log.info("Schema %s found", schema)
            else:
                log.debug("Schemas found: %s %s", *source.list_schemas(True))
                raise RuntimeError(
                    f"Could not find schema {schema} in data dirs: {':'.join(data_dirs)}"
                )
        status.passed()

    @test
    def test_auto_layout(self, status: Status):
        session = self.application.new_session()
        event_manager = session.get_service("event_manager")
        element_factory = session.get_service("element_factory")
        auto_layout = session.get_service("auto_layout")

        with Transaction(event_manager):
            diagram = element_factory.create(Diagram)

        auto_layout.layout(diagram)
        status.passed()


def system_information():
    return textwrap.dedent(
        f"""\
        Gaphor version:         {distribution().version}
        Operating System:       {platform.system()} ({platform.release()}, {platform.machine()})
        Display:                {display_type()}
        Python version:         {platform.python_version()}
        GTK version:            {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}
        Adwaita version:        {Adw.get_major_version()}.{Adw.get_minor_version()}.{Adw.get_micro_version()}
        GtkSourceView version:  {gtk_source_view_version()}
        Cairo version:          {cairo.cairo_version_string()}
        Pango version:          {Pango.version_string()}
        PyGObject version:      {gi.__version__}
        Pycairo version:        {cairo.version}
        """
    )


def display_type():
    dm = Gdk.DisplayManager.get()
    display = dm.get_default_display()
    return display.__class__.__name__ if display else "none"


def gtk_source_view_version():
    if hasattr(GtkSource, "get_major_version"):
        return f"{GtkSource.get_major_version()}.{GtkSource.get_minor_version()}.{GtkSource.get_micro_version()}"
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
