"""The Toolbox which is the tool palette.

This is the toolbox in the lower left of the screen.
"""

import functools
import logging
from typing import Optional, Tuple

from gi.repository import Gdk, GLib, GObject, Gtk

from gaphor.core.eventmanager import EventManager, event_handler
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.diagram.event import ToolCompleted
from gaphor.diagram.tools.dnd import ToolboxActionDragData
from gaphor.services.modelinglanguage import (
    ModelingLanguageChanged,
    ModelingLanguageService,
)
from gaphor.services.properties import Properties
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import CurrentDiagramChanged, ToolSelected

log = logging.getLogger(__name__)


class Toolbox(UIComponent):
    def __init__(
        self,
        event_manager: EventManager,
        properties: Properties,
        modeling_language: ModelingLanguageService,
    ):
        self.event_manager = event_manager
        self.properties = properties
        self.modeling_language = modeling_language
        self._toolbox: Optional[Gtk.Box] = None
        self._toolbox_container: Optional[Gtk.ScrolledWindow] = None
        self._current_diagram_type = ""

    def open(self) -> Gtk.ScrolledWindow:
        self._toolbox = self.create_toolbox(self.modeling_language.toolbox_definition)
        self._toolbox_container = create_toolbox_container(self._toolbox)
        self.event_manager.subscribe(self._on_diagram_item_placed)
        self.event_manager.subscribe(self._on_modeling_language_changed)
        self.event_manager.subscribe(self._on_current_diagram_changed)
        self.select_tool("toolbox-pointer")
        return self._toolbox_container

    def close(self) -> None:
        if self._toolbox:
            if self._toolbox_container:
                self._toolbox_container.unparent()
            self._toolbox = None
        self.event_manager.unsubscribe(self._on_modeling_language_changed)
        self.event_manager.unsubscribe(self._on_diagram_item_placed)
        self.event_manager.unsubscribe(self._on_current_diagram_changed)

    def activate_shortcut(self, keyval: int, state: Gdk.ModifierType) -> bool:
        # Accelerator keys are lower case. Since we handle them in a key-press event
        # handler, we'll need the upper-case versions as well in case Shift is pressed.
        state = state & Gtk.accelerator_get_default_mod_mask()
        for _title, items in self.modeling_language.toolbox_definition:
            for action_name, _label, _icon_name, shortcut, *_rest in items:
                if not shortcut:
                    continue
                keys, mod = parse_shortcut(shortcut)
                if state == mod and keyval in keys:
                    self.select_tool(action_name)
                    return True
        return False

    @property
    def active_tool_name(self):
        for flowbox in self.flowboxes():
            if children := flowbox.get_selected_children():
                return children[0].action_name
        return "toolbox-pointer"

    def create_toolbox(self, toolbox_actions: ToolboxDefinition) -> Gtk.Box:
        toolbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        expanded = self.expanded_sections()

        def on_expanded(widget, _prop, index, revealer):
            expanded = widget.get_property("expanded")
            self.expanded_sections(index, expanded)
            revealer.set_reveal_child(expanded)

        for index, (title, items) in enumerate(toolbox_actions):
            revealer = Gtk.Revealer.new()
            revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
            revealer.set_reveal_child(expanded[index])
            expander = Gtk.Expander.new(title)
            expander.set_property("expanded", expanded[index])
            expander.connect("notify::expanded", on_expanded, index, revealer)
            flowbox = Gtk.FlowBox.new()
            flowbox.set_homogeneous(True)
            flowbox.set_row_spacing(1)
            flowbox.set_column_spacing(1)
            flowbox.set_max_children_per_line(12)
            flowbox.connect("child-activated", self._on_tool_activated)

            drag_source = Gtk.DragSource.new()
            drag_source.connect("prepare", _flowbox_drag_prepare)
            flowbox.add_controller(drag_source)

            for action_name, label, icon_name, shortcut, item_factory, *_rest in items:
                button = create_toolbox_button(
                    action_name, icon_name, label, shortcut, bool(item_factory)
                )
                flowbox.insert(button, -1)

            revealer.set_child(flowbox)
            toolbox.append(expander)
            toolbox.append(revealer)

        return toolbox

    def expanded_sections(self, index=None, state=None):
        diagram_type = self._current_diagram_type or ""
        expanded_property = f"toolbox-{self.modeling_language.active_modeling_language}-{diagram_type}-expanded"
        expanded_sections = next(
            (
                diagram.sections
                for diagram in self.modeling_language.diagram_types
                if diagram.id == diagram_type
            ),
            (),
        )
        default_expanded = {
            i: i == 0 or not bool(expanded_sections)
            for i, _ in enumerate(self.modeling_language.toolbox_definition)
        }
        expanded = default_expanded | self.properties.get(expanded_property, {})

        if index is not None:
            expanded[index] = state
            self.properties.set(expanded_property, expanded)

        required_expanded = {
            i: True
            for i, section in enumerate(self.modeling_language.toolbox_definition)
            if section in expanded_sections
        }
        return expanded | required_expanded

    def flowboxes(self):
        if self._toolbox:
            for expander in iter_children(self._toolbox):
                if isinstance(expander, Gtk.Revealer):
                    yield expander.get_child()

    def select_tool(self, tool_name: str) -> None:
        for flowbox in self.flowboxes():
            flowbox.unselect_all()
            for child in iter_children(flowbox):
                if child.action_name == tool_name:
                    flowbox.select_child(child)
                    self.event_manager.handle(ToolSelected(tool_name))

    @event_handler(ToolCompleted)
    def _on_diagram_item_placed(self, event) -> None:
        if self.properties.get("reset-tool-after-create", True):
            # Select tool from an idle handler, so the original tool can complete properly.
            GLib.idle_add(self.select_tool, "toolbox-pointer")

    @event_handler(ModelingLanguageChanged)
    def _on_modeling_language_changed(self, event: ModelingLanguageChanged) -> None:
        """Reconfigures the toolbox based on the modeling language selected."""
        toolbox = self.create_toolbox(self.modeling_language.toolbox_definition)
        if self._toolbox_container:
            self._toolbox_container.set_child(toolbox)
        self._toolbox = toolbox
        self.select_tool("toolbox-pointer")

    @event_handler(CurrentDiagramChanged)
    def _on_current_diagram_changed(self, event: CurrentDiagramChanged) -> None:
        if not self._toolbox:
            return

        self._current_diagram_type = event.diagram and event.diagram.diagramType or ""

        expanded = self.expanded_sections()
        for index, expander in enumerate(
            c for c in iter_children(self._toolbox) if isinstance(c, Gtk.Expander)
        ):
            expander.set_property("expanded", expanded[index])

    def _on_tool_activated(self, flowbox, child):
        self.select_tool(child.action_name)


def create_toolbox_container(toolbox: Gtk.Widget) -> Gtk.ScrolledWindow:
    toolbox_container = Gtk.ScrolledWindow()
    toolbox_container.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    toolbox_container.set_child(toolbox)
    return toolbox_container


def create_toolbox_button(
    action_name: str,
    icon_name: str,
    label: str,
    shortcut: Optional[str],
    draggable: bool,
) -> Gtk.Button:
    """Creates a tool button for the toolbox."""
    button = Gtk.FlowBoxChild.new()
    icon = Gtk.Image.new_from_icon_name(icon_name)
    button.set_child(icon)
    button.action_name = action_name
    button.icon_name = icon_name
    button.draggable = draggable
    if label:
        if shortcut:
            _, a, m = Gtk.accelerator_parse(shortcut)
            button.set_tooltip_text(f"{label} ({Gtk.accelerator_get_label(a, m)})")
        else:
            button.set_tooltip_text(f"{label}")

    return button


def iter_children(widget):
    child = widget.get_first_child()
    while child:
        yield child
        child = child.get_next_sibling()


def _flowbox_drag_prepare(source: Gtk.DragSource, x: int, y: int):
    child = source.get_widget().get_child_at_pos(x, y)
    if not child.draggable:
        return None

    display = Gdk.Display.get_default()
    theme_icon = Gtk.IconTheme.get_for_display(display).lookup_icon(
        child.icon_name,
        None,
        24,
        1,
        Gtk.TextDirection.NONE,
        Gtk.IconLookupFlags.FORCE_SYMBOLIC,
    )
    source.set_icon(theme_icon, 0, 0)

    v = GObject.Value(
        ToolboxActionDragData.__gtype__,
        ToolboxActionDragData(action=child.action_name),
    )
    return Gdk.ContentProvider.new_for_value(v)


_upper_offset: int = ord("A") - ord("a")


@functools.cache
def parse_shortcut(shortcut: str) -> Tuple[Tuple[int, int], Gdk.ModifierType]:
    _, key, mod = Gtk.accelerator_parse(shortcut)
    return (key, key + _upper_offset), mod
