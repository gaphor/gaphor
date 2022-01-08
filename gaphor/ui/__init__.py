"""This module contains user interface related code, such as the main screen
and diagram windows."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import gi

if os.getenv("GAPHOR_USE_GTK") != "NONE":
    # Allow to explicitly *not* initialize GTK (for docs, mainly)
    gtk_version = "4.0" if os.getenv("GAPHOR_USE_GTK") == "4" else "3.0"
    gtk_source_version = "5" if os.getenv("GAPHOR_USE_GTK") == "4" else "4"

    if gtk_version == "4.0":
        # Monkey patch PyGObject
        import gi.overrides.Gtk

        del gi.overrides.Gtk.TreeView.enable_model_drag_source
        del gi.overrides.Gtk.TreeView.enable_model_drag_dest
        gi.overrides.Gtk.ListStore.insert_with_valuesv = (
            gi.overrides.Gtk.ListStore.insert_with_values
        )

    gi.require_version("Gtk", gtk_version)
    gi.require_version("Gdk", gtk_version)
    if gtk_version == "3.0":
        gi.require_version("GtkSource", gtk_source_version)


from gi.repository import Gdk, Gio, GLib, Gtk

from gaphor.application import Application, Session, distribution
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, ApplicationShutdown, SessionCreated
from gaphor.ui.actiongroup import apply_application_actions
from gaphor.ui.macosshim import macos_init

APPLICATION_ID = "org.gaphor.Gaphor"
HOME = str(Path.home())
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

    if has_option("-v", "--version"):
        print(f"Gaphor {distribution().version}")
        return

    if has_option("-d", "--debug"):
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        logging.getLogger("gaphor").setLevel(logging.DEBUG)
    elif has_option("-q", "--quiet"):
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    if has_option("-p", "--profiler"):

        import cProfile
        import pstats

        with cProfile.Profile() as profile:
            profile.runcall(run, argv)

        profile_stats = pstats.Stats(profile)
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
            application.get_service("greeter").init(gtk_app)
        except Exception:
            gtk_app.quit()
            raise

    def app_activate(gtk_app):
        assert application
        if not application.has_sessions():
            application.get_service("greeter").open()

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
        "version",
        ord("v"),
        GLib.OptionFlags.NONE,
        GLib.OptionArg.NONE,
        "Print version and exit",
        None,
    )
    gtk_app.add_main_option(
        "debug",
        ord("d"),
        GLib.OptionFlags.NONE,
        GLib.OptionArg.NONE,
        "Debug output",
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
