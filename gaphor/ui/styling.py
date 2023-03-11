import importlib

from gi.repository import Gdk, Gtk

from gaphor.abc import Service


class Styling(Service):
    def __init__(self):
        self.style_provider = Gtk.CssProvider()
        css_file = importlib.resources.files("gaphor.ui") / "styling.css"
        self.style_provider.load_from_path(str(css_file))

        self.init_styling()
        self.init_icon_theme()

    def init_styling(self):
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def init_icon_theme(self):
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        path = importlib.resources.files("gaphor.ui") / "icons"
        if icon_theme:
            icon_theme.add_search_path(str(path))

    def shutdown(self):
        Gtk.StyleContext.remove_provider_for_display(
            Gdk.Display.get_default(),
            self.style_provider,
        )
