import functools
import importlib
import logging
from typing import Dict, Optional

from gaphas.guide import GuidePainter
from gaphas.painter import FreeHandPainter, HandlePainter, PainterChain
from gaphas.segment import LineSegmentPainter
from gaphas.tool.rubberband import RubberbandPainter, RubberbandState
from gaphas.view import GtkView
from gi.repository import Gdk, GdkPixbuf, Gtk

from gaphor.core import event_handler, gettext
from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import Diagram, StyledDiagram
from gaphor.core.modeling.event import AttributeUpdated, ElementDeleted
from gaphor.diagram.diagramtoolbox import get_tool_def, tooliter
from gaphor.diagram.drop import drop
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter
from gaphor.diagram.selection import Selection
from gaphor.diagram.tools import (
    apply_default_tool_set,
    apply_magnet_tool_set,
    apply_placement_tool_set,
)
from gaphor.diagram.tools.magnet import MagnetPainter
from gaphor.diagram.tools.placement import create_item, open_editor
from gaphor.event import Notification
from gaphor.transaction import Transaction
from gaphor.ui.event import DiagramClosed, DiagramSelectionChanged, ToolSelected

if Gtk.get_major_version() != 3:
    from gi.repository import Adw


log = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def placement_icon_base():
    f = importlib.resources.files("gaphor") / "ui" / "placement-icon-base.png"
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(str(f), 64, 64, True)


if hasattr(GtkView, "set_css_name"):
    GtkView.set_css_name("diagramview")


if Gtk.get_major_version() == 3:
    _placement_pixbuf_map: Dict[str, GdkPixbuf.Pixbuf] = {}

    def get_placement_cursor(display, icon_name):
        if icon_name in _placement_pixbuf_map:
            pixbuf = _placement_pixbuf_map[icon_name]
        else:
            pixbuf = placement_icon_base().copy()
            icon = Gtk.IconTheme.get_default().load_icon(icon_name, 24, 0)
            icon.copy_area(
                0,
                0,
                icon.get_width(),
                icon.get_height(),
                pixbuf,
                9,
                15,
            )
            _placement_pixbuf_map[icon_name] = pixbuf
        return Gdk.Cursor.new_from_pixbuf(display, pixbuf, 1, 1)

else:

    @functools.lru_cache(maxsize=None)
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
    if Gtk.get_major_version() == 3:
        VIEW_TARGET_STRING = 0
        VIEW_TARGET_ELEMENT_ID = 1
        VIEW_TARGET_TOOLBOX_ACTION = 2
        VIEW_DND_TARGETS = [
            Gtk.TargetEntry.new("gaphor/element-id", 0, VIEW_TARGET_ELEMENT_ID),
            Gtk.TargetEntry.new("gaphor/toolbox-action", 0, VIEW_TARGET_TOOLBOX_ACTION),
        ]

    def __init__(
        self, diagram, event_manager, element_factory, properties, modeling_language
    ):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.properties = properties
        self.diagram = diagram
        self.modeling_language = modeling_language
        self.style_manager = (
            None if Gtk.get_major_version() == 3 else Adw.StyleManager.get_default()
        )

        self.view: Optional[GtkView] = None
        self.widget: Optional[Gtk.Widget] = None
        self.diagram_css: Optional[Gtk.CssProvider] = None

        self.rubberband_state = RubberbandState()
        self._notify_dark_id = (
            self.style_manager.connect("notify::dark", self._on_notify_dark)
            if self.style_manager
            else 0
        )

        self.event_manager.subscribe(self._on_element_delete)
        self.event_manager.subscribe(self._on_attribute_updated)
        self.event_manager.subscribe(self._on_tool_selected)

    title = property(lambda s: s.diagram and s.diagram.name or gettext("<None>"))

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
        if Gtk.get_major_version() == 3:
            view.add_events(Gdk.EventMask.SMOOTH_SCROLL_MASK)
            view.drag_dest_set(
                Gtk.DestDefaults.ALL,
                DiagramPage.VIEW_DND_TARGETS,
                Gdk.DragAction.MOVE | Gdk.DragAction.COPY | Gdk.DragAction.LINK,
            )

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        if Gtk.get_major_version() == 3:
            scrolled_window.add(view)
            scrolled_window.show_all()
            view.connect("drag-data-received", self._on_drag_data_received)
        else:
            scrolled_window.set_child(view)

        view.selection.add_handler(self._on_view_selection_changed)

        self.view = view
        self.widget = scrolled_window

        self.select_tool("toolbox-pointer")

        self.update_drawing_style()

        # Set model only after the painters are set
        view.model = self.diagram

        return self.widget

    def apply_tool_set(self, tool_name):
        """Return a tool associated with an id (action name)."""
        if tool_name == "toolbox-pointer":
            return apply_default_tool_set(
                self.view,
                self.modeling_language,
                self.event_manager,
                self.rubberband_state,
            )
        elif tool_name == "toolbox-magnet":
            return apply_magnet_tool_set(
                self.view,
                self.modeling_language,
                self.event_manager,
            )

        tool_def = get_tool_def(self.modeling_language, tool_name)
        item_factory = tool_def.item_factory
        handle_index = tool_def.handle_index
        return apply_placement_tool_set(
            self.view,
            item_factory=item_factory,
            modeling_language=self.modeling_language,
            event_manager=self.event_manager,
            handle_index=handle_index,
        )

    def get_tool_icon_name(self, tool_name):
        if tool_name in ("toolbox-pointer", "toolbox-magnet"):
            return None
        return next(
            t
            for t in tooliter(self.modeling_language.toolbox_definition)
            if t.id == tool_name
        ).icon_name

    @event_handler(ToolSelected)
    def _on_tool_selected(self, event: ToolSelected):
        self.select_tool(event.tool_name)

    @event_handler(ElementDeleted)
    def _on_element_delete(self, event: ElementDeleted):
        if event.element is self.diagram:
            self.event_manager.handle(DiagramClosed(self.diagram))

    @event_handler(AttributeUpdated)
    def _on_attribute_updated(self, event: AttributeUpdated):
        if event.property is StyleSheet.styleSheet:
            self.update_drawing_style()

            diagram = self.diagram
            for item in diagram.get_all_items():
                diagram.request_update(item)
        elif event.property is Diagram.name and self.view:
            self.view.update_back_buffer()

    def _on_notify_dark(self, style_manager, gparam):
        self.update_drawing_style()

    def close(self):
        """Tab is destroyed.

        Do the same thing that would be done if Close was pressed.
        """
        assert self.widget
        if Gtk.get_major_version() == 3:
            self.widget.destroy()

        if self._notify_dark_id:
            self._notify_dark_id = self.style_manager.disconnect(self._notify_dark_id)  # type: ignore[union-attr]

        self.event_manager.unsubscribe(self._on_element_delete)
        self.event_manager.unsubscribe(self._on_attribute_updated)
        self.event_manager.unsubscribe(self._on_tool_selected)
        self.view = None

    def select_tool(self, tool_name: str):
        if not self.view:
            return
        self.apply_tool_set(tool_name)
        icon_name = self.get_tool_icon_name(tool_name)
        if Gtk.get_major_version() == 3:
            window = self.view.get_window()
            if icon_name and window:
                window.set_cursor(get_placement_cursor(window.get_display(), icon_name))
            elif window:
                window.set_cursor(None)
        elif icon_name:
            self.view.set_cursor(get_placement_cursor(None, icon_name))
        else:
            self.view.set_cursor(None)

    def update_drawing_style(self):
        """Set the drawing style for the diagram based on the active style
        sheet."""
        assert self.view

        dark_mode = self.style_manager.get_dark() if self.style_manager else False
        style = self.diagram.style(StyledDiagram(self.diagram, dark_mode=dark_mode))

        bg = style.get("background-color")
        if bg and bg[3] > 0.0:
            if not self.diagram_css:
                self.diagram_css = Gtk.CssProvider.new()
                self.view.get_style_context().add_provider(
                    self.diagram_css, Gtk.STYLE_PROVIDER_PRIORITY_USER
                )

            self.diagram_css.load_from_data(
                f"diagramview {{ background-color: rgba({int(255*bg[0])}, {int(255*bg[1])}, {int(255*bg[2])}, {bg[3]}); }}".encode()
            )
        else:
            if self.diagram_css:
                self.view.get_style_context().remove_provider(self.diagram_css)
                self.diagram_css = None

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

    def _on_view_selection_changed(self, item):
        view = self.view
        if not view:
            return
        selection = view.selection
        self.event_manager.handle(
            DiagramSelectionChanged(
                view, selection.focused_item, selection.selected_items
            )
        )

    if Gtk.get_major_version() == 3:

        def _on_drag_data_received(self, view, context, x, y, data, info, time):
            """Handle data dropped on the diagram."""
            if (
                data
                and data.get_format() == 8
                and info == DiagramPage.VIEW_TARGET_TOOLBOX_ACTION
            ):
                tool_def = get_tool_def(
                    self.modeling_language, data.get_data().decode()
                )
                with Transaction(self.event_manager):
                    item = create_item(view, tool_def.item_factory, x, y)
                open_editor(item, view, self.event_manager)
                context.finish(True, False, time)
            elif (
                data
                and data.get_format() == 8
                and info == DiagramPage.VIEW_TARGET_ELEMENT_ID
            ):
                element_id = data.get_data().decode()
                element = self.element_factory.lookup(element_id)
                assert element

                x, y = view.matrix.inverse().transform_point(x, y)
                with Transaction(self.event_manager):
                    if item := drop(element, self.diagram, x, y):
                        view.selection.unselect_all()
                        view.selection.focused_item = item

                        context.finish(True, False, time)
                    else:
                        self.event_manager.handle(
                            Notification(
                                gettext("Element can’t be represented on a diagram.")
                            )
                        )
                        context.finish(False, False, time)
            else:
                context.finish(False, False, time)
