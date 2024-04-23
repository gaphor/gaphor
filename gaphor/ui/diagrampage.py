import functools
import importlib
import logging
from typing import Optional

from gaphas.guide import GuidePainter
from gaphas.painter import FreeHandPainter, HandlePainter, PainterChain
from gaphas.segment import LineSegmentPainter
from gaphas.tool.itemtool import find_item_and_handle_at_point
from gaphas.tool.rubberband import RubberbandPainter, RubberbandState
from gaphas.view import GtkView
from gi.repository import Adw, Gdk, GdkPixbuf, Gio, GLib, Gtk

from gaphor.core import event_handler, gettext
from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import Diagram, StyledDiagram
from gaphor.core.modeling.event import AttributeUpdated, ElementDeleted
from gaphor.diagram.diagramtoolbox import get_tool_def, tooliter
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter
from gaphor.diagram.selection import Selection
from gaphor.diagram.tools import (
    apply_default_tool_set,
    apply_magnet_tool_set,
    apply_placement_tool_set,
)
from gaphor.diagram.tools.magnet import MagnetPainter
from gaphor.transaction import Transaction
from gaphor.ui.event import DiagramClosed, ToolSelected

log = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def placement_icon_base():
    f = importlib.resources.files("gaphor") / "ui" / "placement-icon-base.png"
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(str(f), 64, 64, True)


if hasattr(GtkView, "set_css_name"):
    GtkView.set_css_name("diagramview")


@functools.cache
def get_placement_icon(display, icon_name):
    if display is None:
        display = Gdk.Display.get_default()
    pixbuf = placement_icon_base().copy()
    theme_icon = Gtk.IconTheme.get_for_display(display).lookup_icon(
        icon_name,
        None,
        24,
        1,
        Gtk.TextDirection.NONE,
        Gtk.IconLookupFlags.FORCE_SYMBOLIC,
    )
    icon = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        theme_icon.get_file().get_path(), 32, 32, True
    )
    icon.copy_area(
        0,
        0,
        icon.get_width(),
        icon.get_height(),
        pixbuf,
        9,
        15,
    )
    return Gdk.Texture.new_for_pixbuf(pixbuf)


def get_placement_cursor(display, icon_name):
    return Gdk.Cursor.new_from_texture(get_placement_icon(display, icon_name), 1, 1)


class DiagramPage:
    def __init__(self, diagram, event_manager, modeling_language):
        self.event_manager = event_manager
        self.diagram = diagram
        self.modeling_language = modeling_language
        self.style_manager = Adw.StyleManager.get_default()

        self.view: Optional[GtkView] = None
        self.widget: Optional[Gtk.Widget] = None
        self.diagram_css: Optional[Gtk.CssProvider] = None

        self.rubberband_state = RubberbandState()
        self.context_menu = Gtk.PopoverMenu.new_from_model(popup_model(diagram))

        self.event_manager.subscribe(self._on_element_delete)
        self.event_manager.subscribe(self._on_attribute_updated)
        self.event_manager.subscribe(self._on_tool_selected)

    @property
    def title(self):
        return self.diagram and self.diagram.name or gettext("<None>")

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        return self.view

    def construct(self):
        """Create the widget.

        Returns: the newly created widget.
        """
        assert self.diagram

        view = GtkView(selection=Selection())
        view.add_css_class(self._css_class())

        self.diagram_css = Gtk.CssProvider.new()
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.diagram_css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(view)
        scrolled_window.add_css_class("view")
        self.style_manager.connect_object(
            "notify::dark", self._on_notify_dark, scrolled_window
        )

        self.view = view
        self.widget = scrolled_window
        self.context_menu.set_parent(view)

        self.select_tool("toolbox-pointer")

        self.update_drawing_style()

        # Set model only after the painters are set
        view.model = self.diagram

        return self.widget

    def apply_tool_set(self, tool_name):
        """Return a tool associated with an id (action name).

        Tool sets can't be changed if a transaction is active,
        because it could ruin the user (inter)action.
        """

        if Transaction.in_transaction():
            log.warning("Cannot change tool set while in a transaction.")
            return False

        if tool_name == "toolbox-pointer":
            apply_default_tool_set(
                self.view,
                self.modeling_language,
                self.event_manager,
                self.rubberband_state,
            )
            if self.view:
                self.view.add_controller(
                    context_menu_controller(self.context_menu, self.diagram)
                )

        elif tool_name == "toolbox-magnet":
            apply_magnet_tool_set(
                self.view,
                self.modeling_language,
                self.event_manager,
            )
        else:
            tool_def = get_tool_def(self.modeling_language, tool_name)
            item_factory = tool_def.item_factory
            handle_index = tool_def.handle_index
            apply_placement_tool_set(
                self.view,
                item_factory=item_factory,
                modeling_language=self.modeling_language,
                event_manager=self.event_manager,
                handle_index=handle_index,
            )
        return True

    def get_tool_icon_name(self, tool_name):
        if tool_name == "toolbox-pointer":
            return None
        return next(
            t
            for t in tooliter(self.modeling_language.toolbox_definition)
            if t.id == tool_name
        ).icon_name

    def _css_class(self):
        return f"diagram-{id(self)}"

    @event_handler(ToolSelected)
    def _on_tool_selected(self, event: ToolSelected):
        self.select_tool(event.tool_name)

    @event_handler(ElementDeleted)
    def _on_element_delete(self, event: ElementDeleted):
        if event.element is self.diagram:
            self.event_manager.handle(DiagramClosed(self.diagram))

    @event_handler(AttributeUpdated)
    def _on_attribute_updated(self, event: AttributeUpdated):
        if (
            event.property is StyleSheet.styleSheet
            or event.property is StyleSheet.naturalLanguage
        ):
            self.update_drawing_style()

            self.diagram.update(self.diagram.ownedPresentation)
        elif event.property is Diagram.name and self.view:
            self.view.update_back_buffer()

    def _on_notify_dark(self, style_manager, gparam):
        self.update_drawing_style()

    def close(self):
        """Tab is destroyed.

        Do the same thing that would be done if Close was pressed.
        """
        assert self.widget

        Gtk.StyleContext.remove_provider_for_display(
            Gdk.Display.get_default(),
            self.diagram_css,
        )

        self.event_manager.unsubscribe(self._on_element_delete)
        self.event_manager.unsubscribe(self._on_attribute_updated)
        self.event_manager.unsubscribe(self._on_tool_selected)
        self.view = None

    def select_tool(self, tool_name: str):
        if not self.view:
            return

        if self.apply_tool_set(tool_name):
            if icon_name := self.get_tool_icon_name(tool_name):
                self.view.set_cursor(get_placement_cursor(None, icon_name))
            else:
                self.view.set_cursor(None)

    def update_drawing_style(self):
        """Set the drawing style for the diagram based on the active style
        sheet."""
        assert self.view
        assert self.diagram_css

        dark_mode = self.style_manager.get_dark()
        style = self.diagram.style(StyledDiagram(self.diagram, dark_mode=dark_mode))

        bg = style.get("background-color", (0.0, 0.0, 0.0, 0.0))
        self.diagram_css.load_from_string(
            f".{self._css_class()} {{ background-color: rgba({int(255*bg[0])}, {int(255*bg[1])}, {int(255*bg[2])}, {bg[3]}); }}",
        )

        view = self.view
        item_painter = ItemPainter(view.selection, dark_mode)

        if sloppiness := style.get("line-style", 0.0):
            item_painter = FreeHandPainter(item_painter, sloppiness=sloppiness)

        view.bounding_box_painter = item_painter
        view.painter = (
            PainterChain()
            .append(item_painter)
            .append(HandlePainter(view))
            .append(LineSegmentPainter(view.selection))
            .append(GuidePainter(view))
            .append(MagnetPainter(view))
            .append(RubberbandPainter(self.rubberband_state))
            .append(DiagramTypePainter(self.diagram))
        )

        view.request_update(self.diagram.get_all_items())


def context_menu_controller(context_menu, diagram):
    def on_show_popup(ctrl, n_press, x, y):
        if Transaction.in_transaction():
            return

        view = ctrl.get_widget()
        item, _handle = find_item_and_handle_at_point(view, (x, y))

        context_menu.set_menu_model(
            popup_model(item.subject if item and item.subject else diagram)
        )

        gdk_rect = Gdk.Rectangle()
        gdk_rect.x = x
        gdk_rect.y = y
        gdk_rect.width = gdk_rect.height = 1

        context_menu.set_has_arrow(False)
        context_menu.set_pointing_to(gdk_rect)
        context_menu.popup()

    ctrl = Gtk.GestureClick.new()
    ctrl.set_button(Gdk.BUTTON_SECONDARY)
    ctrl.connect("pressed", on_show_popup)
    return ctrl


def popup_model(element):
    model = Gio.Menu.new()
    part = Gio.Menu.new()

    menu_item = Gio.MenuItem.new(
        gettext("Show in Model Browser"),
        "win.show-in-model-browser",
    )
    menu_item.set_attribute_value("target", GLib.Variant.new_string(element.id))

    part.append_item(menu_item)
    model.append_section(None, part)

    return model
