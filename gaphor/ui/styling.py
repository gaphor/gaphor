import importlib

from gi.repository import Gdk, Gtk

from gaphor.abc import Service


class Styling(Service):
    def __init__(self):
        self.style_provider = Gtk.CssProvider()
        with importlib.resources.path(
            "gaphor.ui", f"styling-gtk{Gtk.get_major_version()}.css"
        ) as css_file:
            self.style_provider.load_from_path(str(css_file))

        self.init_styling()
        self.init_icon_theme()

    def init_styling(self):
        if Gtk.get_major_version() == 3:
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                self.style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
        else:
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                self.style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def init_icon_theme(self):
        icon_theme = (
            Gtk.IconTheme.get_default()
            if Gtk.get_major_version() == 3
            else Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        )
        path = importlib.resources.files("gaphor") / "ui" / "icons"
        if icon_theme:
            if Gtk.get_major_version() == 3:
                icon_theme.append_search_path(str(path))
            else:
                icon_theme.add_search_path(str(path))

    def shutdown(self):
        if Gtk.get_major_version() == 3:
            Gtk.StyleContext.remove_provider_for_screen(
                Gdk.Screen.get_default(),
                self.style_provider,
            )
        else:
            Gtk.StyleContext.remove_provider_for_display(
                Gdk.Display.get_default(),
                self.style_provider,
            )
