"""This module contains user interface related code, such as the main screen
and diagram windows."""

# ruff: noqa: E402

from __future__ import annotations

import logging
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GtkSource", "5")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk, GtkSource

import gaphor.asyncio
import gaphor.ui.diagramview  # noqa: F401
import gaphor.ui.textfield  # noqa: F401
from gaphor.application import Application, Session
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, ApplicationShutdown, SessionCreated
from gaphor.i18n import gettext, translated_ui_string
from gaphor.settings import APPLICATION_ID, StyleVariant, settings
from gaphor.storage.recovery import all_sessions
from gaphor.ui.actiongroup import (
    apply_application_actions,
    apply_shortcuts_from_entry_point,
)

Adw.init()
GtkSource.init()

log = logging.getLogger(__name__)


def run(argv: list[str], *, launch_service="greeter", recover=False) -> int:
    application: Application | None = None

    def app_startup(gtk_app):
        nonlocal application

        @event_handler(SessionCreated)
        def on_session_created(event: SessionCreated):
            event_manager = event.session.get_service("event_manager")
            event_manager.subscribe(on_session_changed)
            main_window = event.session.get_service("main_window")
            main_window.open(gtk_app)

        @event_handler(ActiveSessionChanged)
        def on_session_changed(event: ActiveSessionChanged):
            if isinstance(event.service, Session):
                main_window = event.service.get_service("main_window")
                if main_window.window:
                    main_window.window.present()

        @event_handler(ApplicationShutdown)
        def on_quit(_event: ApplicationShutdown):
            gtk_app.quit()

        apply_shortcuts_from_entry_point("gaphor.appservices", "app", gtk_app)
        apply_shortcuts_from_entry_point("gaphor.services", "win", gtk_app)

        try:
            application = Application(gtk_app=gtk_app)
            apply_application_actions(application, gtk_app)

            event_manager = application.get_service("event_manager")
            event_manager.subscribe(on_session_created)
            event_manager.subscribe(on_quit)
            application.get_service(launch_service).init(gtk_app)
            if recover:
                recover_sessions(application)
        except Exception:
            gtk_app.exit_code = 1
            gtk_app.quit()
            raise

    def app_activate(gtk_app):
        assert application
        if not application.sessions:
            application.get_service(launch_service).open()

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

    gtk_app = UIApplication()

    settings.style_variant_changed(update_color_scheme)
    gtk_app.exit_code = 0
    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("open", app_open)

    with gaphor.asyncio.glib_event_loop_policy():
        gtk_app.run(argv)

    return gtk_app.exit_code


def recover_sessions(application):
    for session_id, filename, template in all_sessions():
        if not any(
            session.session_id == session_id for session in application.sessions
        ):
            application.recover_session(
                session_id=session_id, filename=filename, template=template
            )


class UIApplication(Adw.Application):
    def __init__(self):
        # Register session on Darwin, so the NSApplicationDelegate is registered for opening files
        super().__init__(
            application_id=APPLICATION_ID,
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
            register_session=(sys.platform == "darwin"),
        )
        self._menus = {}

    def do_startup(self):
        Adw.Application.do_startup(self)

        builder = Gtk.Builder()
        builder.add_from_string(translated_ui_string("gaphor.ui", "menubar.ui"))
        self.set_menubar(builder.get_object("menu"))
        self._menus["export"] = (gettext("Export"), builder.get_object("export-menu"))
        self._menus["tools"] = (gettext("Tools"), builder.get_object("tools-menu"))

    def update_menu(self, name, submenu):
        hook = self._menus.get(name)
        if hook:
            title, menu = hook
            menu.remove_all()
            menu.append_submenu(title, submenu)
        else:
            log.warning("No submenu with name %s", name)


if __name__ == "__main__":
    run(sys.argv)
