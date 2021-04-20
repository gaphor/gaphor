"""This module contains user interface related code, such as the main screen
and diagram windows."""

import importlib.resources
import logging
import sys
from pathlib import Path
from typing import Optional

from gi.repository import Gdk, Gio, GLib, Gtk

from gaphor.application import Application, Session
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, ApplicationShutdown, SessionCreated
from gaphor.ui.actiongroup import apply_application_actions
from gaphor.ui.macosshim import macos_init

APPLICATION_ID = "org.gaphor.Gaphor"


icon_theme = (
    Gtk.IconTheme.get_default()
    if Gtk.get_major_version() == 3
    else Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
)
if sys.version_info >= (3, 9):
    path: Path = importlib.resources.files("gaphor") / "ui" / "icons"
    if Gtk.get_major_version() == 3:
        icon_theme.append_search_path(str(path))
    else:
        icon_theme.add_search_path(str(path))
else:
    with importlib.resources.path("gaphor.ui", "icons") as path:
        if Gtk.get_major_version() == 3:
            icon_theme.append_search_path(str(path))
        else:
            icon_theme.add_search_path(str(path))

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv=sys.argv):
    """Start Gaphor from the command line.  This function creates an option
    parser for retrieving arguments and options from the command line.  This
    includes a Gaphor model to load.

    The application is then initialized, passing along the option
    parser.  This provides plugins and services with access to the
    command line options and may add their own.
    """

    def has_option(*options):
        return any(o in argv for o in options)

    if has_option("-v", "--verbose"):
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        logging.getLogger("gaphor").setLevel(logging.DEBUG)
    elif has_option("-q", "--quiet"):
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    if has_option("-p", "--profiler"):

        import cProfile
        import pstats

        cProfile.runctx(
            "run(argv)",
            globals(),
            locals(),
            filename="gaphor.prof",
        )

        profile_stats = pstats.Stats("gaphor.prof")
        profile_stats.strip_dirs().sort_stats("time").print_stats(50)

    else:
        run(argv)


def run(args):
    application: Optional[Application] = None

    def app_startup(gtk_app):
        nonlocal application

        @event_handler(SessionCreated)
        def on_session_created(event):
            event_manager = event.session.get_service("event_manager")
            event_manager.subscribe(on_session_changed)
            main_window = event.session.get_service("main_window")
            main_window.open(gtk_app)

        @event_handler(ActiveSessionChanged)
        def on_session_changed(event):
            if isinstance(event.service, Session):
                main_window = event.service.get_service("main_window")
                if main_window.window:
                    main_window.window.present_with_time(Gdk.CURRENT_TIME)

        @event_handler(ApplicationShutdown)
        def on_quit(event):
            gtk_app.quit()

        try:
            application = Application()
            apply_application_actions(application, gtk_app)
            if macos_init:
                macos_init(application)
            event_manager = application.get_service("event_manager")
            event_manager.subscribe(on_session_created)
            event_manager.subscribe(on_quit)
        except Exception:
            gtk_app.quit()
            raise

    def app_activate(gtk_app):
        assert application
        if not application.has_sessions():
            application.new_session()

    def app_open(gtk_app, files, n_files, hint):
        # appfilemanager should take care of this:
        assert application
        if hint == "__new__":
            application.new_session()
        else:
            for file in files:
                application.new_session(filename=file.get_path())

    gtk_app = Gtk.Application(
        application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN
    )
    add_main_options(gtk_app)
    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("open", app_open)
    gtk_app.run(args)


def add_main_options(gtk_app):
    """These parameters are handled in `gaphor.ui.main()`.

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
