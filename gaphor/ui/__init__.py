"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

import importlib.resources
import logging
import sys

import gi

from gaphor.application import Application, Session
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

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv=sys.argv):
    """Start Gaphor from the command line.  This function creates an option
    parser for retrieving arguments and options from the command line.  This
    includes a Gaphor model to load.

    The application is then initialized, passing along the option parser.  This
    provides plugins and services with access to the command line options
    and may add their own."""

    def has_option(*options):
        return any(o in argv for o in options)

    if has_option("-v", "--verbose"):
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    elif has_option("-q", "--quiet"):
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    if has_option("-p", "--profiler"):

        import cProfile
        import pstats

        cProfile.runctx(
            "run(argv)", globals(), locals(), filename="gaphor.prof",
        )

        profile_stats = pstats.Stats("gaphor.prof")
        profile_stats.strip_dirs().sort_stats("time").print_stats(50)

    else:
        run(argv)


def run(args):
    gtk_app = Gtk.Application(
        application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN
    )
    add_main_options(gtk_app)

    def app_startup(app):
        pass  # Application.init()

    def app_activate(app):
        # Make sure gui is loaded ASAP.
        # This prevents menu items from appearing at unwanted places.
        # main_window = application.get_service("main_window")
        # main_window.open(app)
        # app.add_window(main_window.window)

        if not Application.has_sessions():
            session = Application.init()

            # Only at application level (startup())?
            component_registry = session.get_service("component_registry")
            apply_application_actions(component_registry, app)

            main_window = session.get_service("main_window")
            main_window.open(app)
            app.add_window(main_window.window)

            file_manager = session.get_service("file_manager")
            file_manager.action_new()

    def app_open(app, files, n_files, hint):
        print(f"Open files {files} with '{hint}'.")
        assert n_files == 1
        for file in files:
            session = Application.init()
            component_registry = session.get_service("component_registry")
            apply_application_actions(component_registry, app)

            main_window = session.get_service("main_window")
            main_window.open(app)
            app.add_window(main_window.window)

            file_manager = Application.get_service("file_manager")
            file_manager.load(file.get_path())

    def app_shutdown(app):
        Application.shutdown()

    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("open", app_open)
    gtk_app.connect("shutdown", app_shutdown)
    gtk_app.run(args)


def quit():
    Gtk.Application.get_default().quit()


def add_main_options(gtk_app):
    """
    These parameters are handled in `gaphor.ui.main()`.
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
