"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

import importlib.resources

import gi

from gaphor.ui.actiongroup import apply_application_actions

# fmt: off
gi.require_version("Gtk", "3.0")  # noqa: isort:skip
gi.require_version("Gdk", "3.0")  # noqa: isort:skip
from gi.repository import GLib, Gdk, Gio, Gtk  # noqa: isort:skip
# fmt: on


APPLICATION_ID = "org.gaphor.Gaphor"


icon_theme = Gtk.IconTheme.get_default()
with importlib.resources.path("gaphor.ui", "icons") as path:
    icon_theme.append_search_path(str(path))


def run(application, args):
    gtk_app = Gtk.Application(
        application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN
    )
    add_main_options(gtk_app)

    def app_startup(app):
        application.init()

        component_registry = application.get_service("component_registry")
        apply_application_actions(component_registry, app)

        main_window = application.get_service("main_window")
        main_window.open(app)
        app.add_window(main_window.window)

    def app_activate(app):
        # Make sure gui is loaded ASAP.
        # This prevents menu items from appearing at unwanted places.
        # main_window = application.get_service("main_window")
        # main_window.open(app)
        # app.add_window(main_window.window)

        file_manager = application.get_service("file_manager")
        file_manager.action_new()

    def app_open(app, files, n_files, hint):
        print(f"Open files {files} with '{hint}'.")
        assert n_files == 1
        for file in files:
            # main_window = application.get_service("main_window")
            # main_window.open(app)
            # app.add_window(main_window.window)

            file_manager = application.get_service("file_manager")
            file_manager.load(file.get_path())

    def app_shutdown(app):
        application.shutdown()

    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("open", app_open)
    gtk_app.connect("shutdown", app_shutdown)
    gtk_app.run(args)


def quit():
    Gtk.Application.get_default().quit()


def add_main_options(gtk_app):
    """
    These parameters are handled in `gaphor.main()` (`gaphor/__init__.py`).
    Define them here, so they show up on `gaphor --help`.
    """
    gtk_app.add_main_option(
        "verbose",
        ord("v"),
        GLib.OptionFlags.NONE,
        GLib.OptionArg.NONE,
        "Verbose output",
        None,
    )
    gtk_app.add_main_option(
        "quiet",
        ord("q"),
        GLib.OptionFlags.NONE,
        GLib.OptionArg.NONE,
        "Quiet output",
        None,
    )
    gtk_app.add_main_option(
        "profiler",
        ord("p"),
        GLib.OptionFlags.NONE,
        GLib.OptionArg.NONE,
        "Run in profiler",
        None,
    )
