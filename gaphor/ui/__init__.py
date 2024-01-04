"""This module contains user interface related code, such as the main screen
and diagram windows."""

# ruff: noqa: E402,F401

from __future__ import annotations

import sys
import warnings

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GtkSource", "5")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, GtkSource

import gaphor.ui.textfield
from gaphor.application import Application, Session
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, ApplicationShutdown, SessionCreated
from gaphor.settings import APPLICATION_ID, StyleVariant, settings
from gaphor.ui.actiongroup import apply_application_actions

Adw.init()
GtkSource.init()

if sys.platform == "darwin":
    from gaphor.ui.macosshim import init_macos_shortcuts

    try:
        init_macos_shortcuts()
    except TypeError:
        # Initialization can fail if Gtk is mocked
        warnings.warn(
            "macOS shortcuts were not initialized", RuntimeWarning, stacklevel=1
        )


def run(argv: list[str]) -> int:
    application: Application | None = None

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
                    main_window.window.present()

        @event_handler(ApplicationShutdown)
        def on_quit(_event):
            gtk_app.quit()

        try:
            application = Application(gtk_app=gtk_app)
            apply_application_actions(application, gtk_app)
            event_manager = application.get_service("event_manager")
            event_manager.subscribe(on_session_created)
            event_manager.subscribe(on_quit)
            application.get_service(
                "self_test" if "--self-test" in argv else "greeter"
            ).init(gtk_app)
        except Exception:
            gtk_app.exit_code = 1
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

    def update_color_scheme(style_variant: StyleVariant):
        gtk_app.get_style_manager().set_color_scheme(
            {
                StyleVariant.DARK: Adw.ColorScheme.FORCE_DARK,
                StyleVariant.LIGHT: Adw.ColorScheme.FORCE_LIGHT,
            }.get(style_variant, Adw.ColorScheme.DEFAULT)
        )

    # Register session on Darwin, so the NSApplicationDelegate is registered for opening files
    gtk_app = Adw.Application(
        application_id=APPLICATION_ID,
        flags=Gio.ApplicationFlags.HANDLES_OPEN,
        register_session=(sys.platform == "darwin"),
    )

    settings.style_variant_changed(update_color_scheme)
    gtk_app.exit_code = 0
    add_main_options(gtk_app)
    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("open", app_open)
    gtk_app.run(argv)
    return gtk_app.exit_code


def add_main_options(gtk_app):
    """These parameters are handled in `gaphor.ui.run()`."""
    gtk_app.add_main_option(
        "self-test",
        0,
        GLib.OptionFlags.NONE,
        GLib.OptionArg.NONE,
        "Run self test and exit",
        None,
    )


if __name__ == "__main__":
    run(sys.argv)
