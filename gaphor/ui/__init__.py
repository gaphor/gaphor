"""
This module contains user interface related code, such as the
main screen and diagram windows.
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk
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
