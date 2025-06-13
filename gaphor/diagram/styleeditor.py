from gi.repository import Gdk, Gtk

from gaphor.core import event_handler
from gaphor.core.modeling import (
    AttributeUpdated,
    ElementDeleted,
    Presentation,
    StyleSheet,
    css_name,
)
from gaphor.core.modeling.diagram import StyledItem
from gaphor.core.styling import Color, Style
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder
from gaphor.i18n import translated_ui_string
from gaphor.transaction import Transaction


@PropertyPages.register(Presentation)
class StylePropertyPage(PropertyPageBase):
    """A button to open a easy-to-use CSS editor."""

    order = 450
    style_editor = None

    def __init__(self, subject, event_manager, element_factory, main_window):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.main_window = main_window
        self.watcher = subject.watcher() if subject else None
        self.propertypages_builder = new_builder(
            "style-editor",
            signals={
                "open-style-editor": (self._on_open_style_editor,),
            },
        )

    def construct(self):
        if not self.subject:
            return
        assert self.watcher
        return self.propertypages_builder.get_object("style-editor")

    def _on_open_style_editor(self, button):
        if StylePropertyPage.style_editor:
            StylePropertyPage.style_editor.close()

        style_sheet = self.element_factory.style_sheet
        StylePropertyPage.style_editor = StyleEditor(
            self.subject,
            style_sheet,
            self.event_manager,
            self.main_window.window,
            self.close_style_editor,
        )
        StylePropertyPage.style_editor.present()

    def close_style_editor(self):
        StylePropertyPage.style_editor = None


class StyleEditor:
    def __init__(
        self,
        subject: Presentation,
        style_sheet: StyleSheet,
        event_manager,
        parent_window,
        close_callback,
    ):
        self.subject = subject
        self.style_sheet = style_sheet
        self.event_manager = event_manager
        self.parent_window = parent_window
        self.close_callback = close_callback

        self.window_builder = Gtk.Builder()
        self.window_builder.add_from_string(
            translated_ui_string("gaphor.diagram", "styleeditor.ui")
        )

        self.window: Gtk.Window | None = None
        self.presentation_style: Style = {}

        event_manager.subscribe(self._on_name_changed)
        event_manager.subscribe(self._on_element_deleted)

    def present(self):
        if self.window is None:
            self.window = self.window_builder.get_object("style-editor")
            self.window.connect("close-request", self.close)
            self.color = self.window_builder.get_object("color")
            self.border_radius = self.window_builder.get_object("border-radius")
            self.background_color = self.window_builder.get_object("background-color")
            self.text_color = self.window_builder.get_object("text-color")
            self.window.set_transient_for(self.parent_window)

            self.fields()

            self.color.connect("notify::rgba", self.on_color_set)
            self.border_radius.connect("value-changed", self.on_border_radius_set)
            self.background_color.connect("notify::rgba", self.on_background_color_set)
            self.text_color.connect("notify::rgba", self.on_text_color_set)
            self.window_builder.get_object("export").connect("clicked", self.on_export)

        self.window.present()

    def fields(self):
        style = self.style_sheet.compute_style(StyledItem(self.subject))
        if style.get("color"):
            self.color.set_rgba(to_gdk_rgba(style["color"]))
            self.text_color.set_rgba(to_gdk_rgba(style["color"]))

        if style.get("border-radius"):
            self.border_radius.set_value(int(style["border-radius"]))

        if style.get("background-color"):
            self.background_color.set_rgba(to_gdk_rgba(style["background-color"]))

        if style.get("text-color"):
            self.text_color.set_rgba(to_gdk_rgba(style["text-color"]))

    def close(self, _widget=None):
        if self.window:
            self.window.destroy()
            self.window = None
        self.event_manager.subscribe(self._on_name_changed)
        self.style_sheet.instant_style_declarations = ""
        self.close_callback()

    def change_style(self, prop, value):
        self.presentation_style[prop] = value  # type: ignore[literal-required]
        self.style_sheet.instant_style_declarations = self.render_css()

    def on_color_set(self, widget, _paramspec=None):
        color = widget.get_rgba()
        self.change_style("color", from_gdk_rgba(color))

    def on_border_radius_set(self, widget):
        self.change_style("border-radius", widget.get_value())

    def on_background_color_set(self, widget, _paramspec=None):
        color = widget.get_rgba()
        self.change_style("background-color", from_gdk_rgba(color))

    def on_text_color_set(self, widget, _paramspec=None):
        color = widget.get_rgba()
        self.change_style("text-color", from_gdk_rgba(color))

    def on_export(self, _widget):
        with Transaction(self.event_manager):
            self.style_sheet.styleSheet += f"\n{self.render_css()}\n"
        self.close()

    @event_handler(AttributeUpdated)
    def _on_name_changed(self, event: AttributeUpdated):
        if event.property.name == "name":
            self.style_sheet.instant_style_declarations = self.render_css()

    @event_handler(ElementDeleted)
    def _on_element_deleted(self, event: ElementDeleted):
        if event.element is self.subject:
            self.close()

    def render_css(self) -> str:
        name = getattr(self.subject.subject, "name", None)
        tag = css_name(self.subject)
        selector = f'{tag}[name="{name}"]' if name else tag
        properties = "\n".join(
            f"  {k}: {v};" for k, v in self.presentation_style.items()
        )
        return f"{selector} {{\n{properties}\n}}"


def to_gdk_rgba(color: str | Color) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    if isinstance(color, str):
        rgba.parse(color)
    else:
        rgba.red, rgba.green, rgba.blue, rgba.alpha = color
    return rgba


def from_gdk_rgba(rgba: Gdk.RGBA) -> str:
    r = int(rgba.red * 255)
    g = int(rgba.green * 255)
    b = int(rgba.blue * 255)
    a = rgba.alpha
    return f"rgba({r}, {g}, {b}, {a})"
