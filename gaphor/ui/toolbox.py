"""The Toolbox which is the tool palette.

This is the toolbox in the lower left of the screen.
"""

import functools
import logging
from typing import Optional, Tuple

from gi.repository import Gdk, GObject, Gtk

from gaphor.core.eventmanager import EventManager, event_handler
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.diagram.event import ToolCompleted
from gaphor.diagram.hoversupport import flowbox_add_hover_support
from gaphor.event import TransactionCommit
from gaphor.services.modelinglanguage import (
    ModelingLanguageChanged,
    ModelingLanguageService,
)
from gaphor.services.properties import Properties
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import CurrentDiagramChanged, ToolSelected

log = logging.getLogger(__name__)


class Toolbox(UIComponent):

    if Gtk.get_major_version() == 3:
        TARGET_STRING = 0
        TARGET_TOOLBOX_ACTION = 1
        DND_TARGETS = [
            Gtk.TargetEntry.new("STRING", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
            Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
            Gtk.TargetEntry.new(
                "gaphor/toolbox-action", Gtk.TargetFlags.SAME_APP, TARGET_TOOLBOX_ACTION
            ),
        ]

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
            if Gtk.get_major_version() == 3:
                self._toolbox.destroy()
            elif self._toolbox_container:
                self._toolbox_container.unparent()
            self._toolbox = None
        self.event_manager.unsubscribe(self._on_modeling_language_changed)
        self.event_manager.unsubscribe(self._on_diagram_item_placed)
        self.event_manager.unsubscribe(self._on_current_diagram_changed)

    def activate_shortcut(self, keyval: int, state: Gdk.ModifierType) -> bool:
        # Accelerator keys are lower case. Since we handle them in a key-press event
        # handler, we'll need the upper-case versions as well in case Shift is pressed.
        for _title, items in self.modeling_language.toolbox_definition:
            for action_name, _label, _icon_name, shortcut, *rest in items:
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
            children = flowbox.get_selected_children()
            if children:
                return children[0].action_name
        return "toolbox-pointer"

    def create_toolbox(self, toolbox_actions: ToolboxDefinition) -> Gtk.Box:
        toolbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        toolbox.set_name("toolbox")
        expanded = self.expanded_sections()

        def on_expanded(widget, _prop, index):
            self.expanded_sections(index, widget.get_property("expanded"))

        for index, (title, items) in enumerate(toolbox_actions):
            expander = Gtk.Expander.new(title)
            expander.set_property("expanded", expanded[index])
            expander.connect("notify::expanded", on_expanded, index)
            flowbox = Gtk.FlowBox.new()
            flowbox.set_homogeneous(True)
            flowbox.set_max_children_per_line(12)
            flowbox_add_hover_support(flowbox)
            flowbox.connect("child-activated", self._on_tool_activated)

            if Gtk.get_major_version() == 3:
                # Enable Drag and Drop
                flowbox.drag_source_set(
                    Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
                    self.DND_TARGETS,
                    Gdk.DragAction.COPY | Gdk.DragAction.LINK,
                )
                flowbox.connect("drag-begin", _flowbox_drag_begin)
                flowbox.connect("drag-data-get", _flowbox_drag_data_get)
            else:
                drag_source = Gtk.DragSource.new()
                drag_source.connect("prepare", _flowbox_drag_prepare)
                flowbox.add_controller(drag_source)

            if Gtk.get_major_version() == 3:
                expander.add(flowbox)
            else:
                expander.set_child(flowbox)
            for action_name, label, icon_name, shortcut, *rest in items:
                button = create_toolbox_button(action_name, icon_name, label, shortcut)
                flowbox.insert(button, -1)

            if Gtk.get_major_version() == 3:
                toolbox.add(expander)
            else:
                toolbox.append(expander)

        if Gtk.get_major_version() == 3:
            toolbox.show_all()
        return toolbox

    def expanded_sections(self, index=None, state=None):
        diagram_type = self._current_diagram_type or ""
        expanded_property = f"toolbox-{self.modeling_language.active_modeling_language}-{diagram_type}-expanded"
        expanded_sections = next(
            (
                sections
                for id, _, sections in self.modeling_language.diagram_types
                if id == diagram_type
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
                yield expander.get_child()

    def select_tool(self, tool_name: str) -> None:
        for flowbox in self.flowboxes():
            for child in iter_children(flowbox):
                if child.action_name == tool_name:
                    flowbox.select_child(child)
                    for fb in self.flowboxes():
                        if fb is not flowbox:
                            fb.unselect_all()
                    self.event_manager.handle(ToolSelected(tool_name))
                    return

    @event_handler(ToolCompleted)
    def _on_diagram_item_placed(self, event: TransactionCommit) -> None:
        if self.properties.get("reset-tool-after-create", True):
            self.select_tool("toolbox-pointer")

    @event_handler(ModelingLanguageChanged)
    def _on_modeling_language_changed(self, event: ModelingLanguageChanged) -> None:
        """Reconfigures the toolbox based on the modeling language selected."""
        toolbox = self.create_toolbox(self.modeling_language.toolbox_definition)
        if self._toolbox_container:
            if Gtk.get_major_version() == 3:
                self._toolbox_container.remove(self._toolbox_container.get_child())
                self._toolbox_container.add(toolbox)
            else:
                self._toolbox_container.set_child(toolbox)
        self._toolbox = toolbox
        self.select_tool("toolbox-pointer")

    @event_handler(CurrentDiagramChanged)
    def _on_current_diagram_changed(self, event: CurrentDiagramChanged) -> None:
        if not self._toolbox:
            return

        self._current_diagram_type = event.diagram and event.diagram.diagramType or ""

        expanded = self.expanded_sections()
        for index, expander in enumerate(iter_children(self._toolbox)):
            expander.set_property("expanded", expanded[index])

    def _on_tool_activated(self, flowbox, child):
        self.select_tool(child.action_name)


def create_toolbox_container(toolbox: Gtk.Widget) -> Gtk.ScrolledWindow:
    toolbox_container = Gtk.ScrolledWindow()
    toolbox_container.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    if Gtk.get_major_version() == 3:
        toolbox_container.add(toolbox)
        toolbox_container.show()
    else:
        toolbox_container.set_child(toolbox)
    return toolbox_container


def create_toolbox_button(
    action_name: str, icon_name: str, label: str, shortcut: Optional[str]
) -> Gtk.Button:
    """Creates a tool button for the toolbox."""
    button = Gtk.FlowBoxChild.new()
    if Gtk.get_major_version() == 3:
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        button.add(icon)
    else:
        icon = Gtk.Image.new_from_icon_name(icon_name)
        button.set_child(icon)
    button.action_name = action_name
    button.icon_name = icon_name
    if label:
        if shortcut:
            if Gtk.get_major_version() == 3:
                a, m = Gtk.accelerator_parse(shortcut)
            else:
                _, a, m = Gtk.accelerator_parse(shortcut)
            button.set_tooltip_text(f"{label} ({Gtk.accelerator_get_label(a, m)})")
        else:
            button.set_tooltip_text(f"{label}")

    return button


if Gtk.get_major_version() == 3:

    def iter_children(widget):
        yield from widget.get_children()

    def _flowbox_drag_begin(flowbox: Gtk.FlowBox, context: Gdk.DragContext) -> None:
        event = Gtk.get_current_event()
        assert event
        child = flowbox.get_child_at_pos(event.x, event.y)
        flowbox.drag_source_set_icon_name(child.icon_name)
        flowbox._dnd_child = child

    def _flowbox_drag_data_get(
        flowbox: Gtk.FlowBox,
        context: Gdk.DragContext,
        data: Gtk.SelectionData,
        info: int,
        time: int,
    ) -> None:
        """The drag-data-get event signal handler.

        The drag-data-get signal is emitted on the drag source when the
        drop site requests the data which is dragged.
        """
        data.set(
            type=data.get_target(),
            format=8,
            data=flowbox._dnd_child.action_name.encode(),
        )

else:

    def iter_children(widget):
        child = widget.get_first_child()
        while child:
            yield child
            child = child.get_next_sibling()

    def _flowbox_drag_prepare(source: Gtk.DragSource, x: int, y: int):
        child = source.get_widget().get_child_at_pos(x, y)

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

        v = GObject.Value(GObject.TYPE_STRING)
        v.set_string(child.action_name)
        return Gdk.ContentProvider.new_for_value(v)


_upper_offset: int = ord("A") - ord("a")


@functools.lru_cache(maxsize=None)
def parse_shortcut(shortcut: str) -> Tuple[Tuple[int, int], Gdk.ModifierType]:
    if Gtk.get_major_version() == 3:
        key, mod = Gtk.accelerator_parse(shortcut)
    else:
        _, key, mod = Gtk.accelerator_parse(shortcut)
    return (key, key + _upper_offset), mod
