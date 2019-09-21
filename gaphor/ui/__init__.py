"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gio, Gtk, Gdk
import importlib.resources
import os.path

icon_theme = Gtk.IconTheme.get_default()
with importlib.resources.path("gaphor.ui", "pixmaps") as path:
    icon_theme.append_search_path(str(path))


# Set style for model canvas
css_provider = Gtk.CssProvider.new()
screen = Gdk.Display.get_default().get_default_screen()

Gtk.StyleContext.add_provider_for_screen(
    screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
css_provider.load_from_data(b"#diagram-tab { background: white }")


def run(application, model):
    gtk_app = Gtk.Application(
        application_id="org.gaphor.Gaphor", flags=Gio.ApplicationFlags.FLAGS_NONE
    )

    def app_startup(app):
        application.init()

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

    def app_quit(action, param):
        file_manager = application.get_service("file_manager")
        return file_manager.file_quit()

    action = Gio.SimpleAction.new("quit", None)
    action.connect("activate", app_quit)
    gtk_app.add_action(action)

    gtk_app.connect("startup", app_startup)
    gtk_app.connect("activate", app_activate)
    gtk_app.connect("shutdown", app_shutdown)
    gtk_app.run()


def quit():
    Gtk.Application.get_default().quit()
