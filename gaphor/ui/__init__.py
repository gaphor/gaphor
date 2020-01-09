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
from gi.repository import Gdk, Gio, Gtk  # noqa: isort:skip
# fmt: on


APPLICATION_ID = "org.gaphor.Gaphor"


icon_theme = Gtk.IconTheme.get_default()
with importlib.resources.path("gaphor.ui", "icons") as path:
    icon_theme.append_search_path(str(path))


def run(application, model):
    gtk_app = Gtk.Application(
        application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.FLAGS_NONE
    )

    def app_startup(app):
        application.init()

        component_registry = application.get_service("component_registry")
        apply_application_actions(component_registry, app)

    def app_activate(app):
        # Make sure gui is loaded ASAP.
        # This prevents menu items from appearing at unwanted places.
        main_window = application.get_service("main_window")
        main_window.open(app)
        app.add_window(main_window.window)

        file_manager = application.get_service("file_manager")

        if model:
            file_manager.load(model)
        else:
            file_manager.action_new()

    def app_shutdown(app):
        application.shutdown()

    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("shutdown", app_shutdown)
    gtk_app.run()


def quit():
    Gtk.Application.get_default().quit()
