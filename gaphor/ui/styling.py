import importlib
import sys

from gi.repository import Gdk, Gtk

from gaphor.abc import Service


class Styling(Service):
    def __init__(self):
        self.style_provider = init_styling()
        init_icon_theme()

    def shutdown(self):
        Gtk.StyleContext.remove_provider_for_display(
            Gdk.Display.get_default(),
            self.style_provider,
        )


def init_styling():
    style_provider = Gtk.CssProvider()
    css = (importlib.resources.files("gaphor.ui") / "styling.css").read_text(
        encoding="utf-8"
    )
    if sys.platform in ("darwin", "win32"):
        css += (
            importlib.resources.files("gaphor.ui") / "styling-box-shadow.css"
        ).read_text(encoding="utf-8")
    style_provider.load_from_string(css)

    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
    return style_provider


def init_icon_theme():
    icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
    path = importlib.resources.files("gaphor.ui") / "icons"
    if icon_theme:
        icon_theme.add_search_path(str(path))
