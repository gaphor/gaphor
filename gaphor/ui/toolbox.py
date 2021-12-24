"""The Toolbox which is the tool palette.

This is the toolbox in the lower left of the screen.
"""

import functools
import logging
from typing import Optional, Tuple

from gi.repository import Gdk, GLib, Gtk

from gaphor.core import action
from gaphor.core.eventmanager import EventManager, event_handler
from gaphor.diagram.diagramtoolbox import ToolboxDefinition
from gaphor.event import TransactionCommit
from gaphor.services.modelinglanguage import (
    ModelingLanguageChanged,
    ModelingLanguageService,
)
from gaphor.services.properties import Properties
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import create_action_group, from_variant
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
        self._action_group, _ = create_action_group(self, "toolbox")
        self._toolbox: Optional[Gtk.Box] = None
        self._toolbox_container: Optional[Gtk.ScrolledWindow] = None
        self._current_diagram_type = ""

    def open(self) -> Gtk.ScrolledWindow:
        toolbox = self.create_toolbox(self.modeling_language.toolbox_definition)
        toolbox_container = self.create_toolbox_container(toolbox)
        self.event_manager.subscribe(self._on_diagram_item_placed)
        self.event_manager.subscribe(self._on_modeling_language_changed)
        self.event_manager.subscribe(self._on_current_diagram_changed)
        self._toolbox = toolbox
        self._toolbox_container = toolbox_container
        return toolbox_container

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
                    self._action_group.activate_action(
                        "select-tool", GLib.Variant.new_string(action_name)
                    )
                    return True
        return False

    @property
    def active_tool_name(self):
        gvar = self._action_group.get_action_state("select-tool")
        return gvar and from_variant(gvar)

    def create_toolbox_button(
        self, action_name: str, icon_name: str, label: str, shortcut: Optional[str]
    ) -> Gtk.Button:
        """Creates a tool button for the toolbox."""
        button = Gtk.ToggleButton.new()
        if Gtk.get_major_version() == 3:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            button.add(icon)
        else:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            button.set_child(icon)
        button.set_action_name("toolbox.select-tool")
        button.set_action_target_value(GLib.Variant.new_string(action_name))
        button.get_style_context().add_class("flat")
        if label:
            if shortcut:
                if Gtk.get_major_version() == 3:
                    a, m = Gtk.accelerator_parse(shortcut)
                else:
                    _, a, m = Gtk.accelerator_parse(shortcut)
                button.set_tooltip_text(f"{label} ({Gtk.accelerator_get_label(a, m)})")
            else:
                button.set_tooltip_text(f"{label}")

        # Enable Drag and Drop
        if (
            action_name not in ("toolbox-pointer", "toolbox-magnet")
            and Gtk.get_major_version() == 3
        ):
            button.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
                self.DND_TARGETS,
                Gdk.DragAction.COPY | Gdk.DragAction.LINK,
            )
            button.drag_source_set_icon_name(icon_name)
            button.connect("drag-data-get", _button_drag_data_get, action_name)
        return button

    def create_toolbox(self, toolbox_actions: ToolboxDefinition) -> Gtk.Box:
        toolbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        toolbox.set_name("toolbox")
        toolbox.connect("destroy", self._on_toolbox_destroyed)
        toolbox.insert_action_group("toolbox", self._action_group)
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
            if Gtk.get_major_version() == 3:
                expander.add(flowbox)
            else:
                expander.set_child(flowbox)
            for action_name, label, icon_name, shortcut, *rest in items:
                button = self.create_toolbox_button(
                    action_name, icon_name, label, shortcut
                )
                flowbox.insert(button, -1)

            if Gtk.get_major_version() == 3:
                toolbox.add(expander)
            else:
                toolbox.append(expander)

        if Gtk.get_major_version() == 3:
            toolbox.show_all()
        return toolbox

    def create_toolbox_container(self, toolbox: Gtk.Widget) -> Gtk.ScrolledWindow:
        toolbox_container = Gtk.ScrolledWindow()
        toolbox_container.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        if Gtk.get_major_version() == 3:
            toolbox_container.add(toolbox)
            toolbox_container.show()
        else:
            toolbox_container.set_child(toolbox)
        return toolbox_container

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

    @action(name="toolbox.select-tool", state="toolbox-pointer")
    def select_tool(self, tool_name: str) -> None:
        self.event_manager.handle(ToolSelected(tool_name))

    @event_handler(TransactionCommit)
    def _on_diagram_item_placed(self, event: TransactionCommit) -> None:
        if self.properties.get("reset-tool-after-create", True):
            self._action_group.lookup_action("select-tool").activate(
                GLib.Variant.new_string("toolbox-pointer")
            )

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

    @event_handler(CurrentDiagramChanged)
    def _on_current_diagram_changed(self, event: CurrentDiagramChanged) -> None:
        self._current_diagram_type = event.diagram and event.diagram.diagramType or ""

        toolbox = self._toolbox_container.get_child().get_child()  # type: ignore[union-attr]
        expanded = self.expanded_sections()
        for index, expander in enumerate(toolbox.get_children()):
            expander.set_property("expanded", expanded[index])

    def _on_toolbox_destroyed(self, widget: Gtk.Widget) -> None:
        self._toolbox = None


if Gtk.get_major_version() == 3:

    def _button_drag_data_get(
        button: Gtk.Button,
        context: Gdk.DragContext,
        data: Gtk.SelectionData,
        info: int,
        time: int,
        action_name: str,
    ) -> None:
        """The drag-data-get event signal handler.

        The drag-data-get signal is emitted on the drag source when the
        drop site requests the data which is dragged.
        """
        data.set(type=data.get_target(), format=8, data=action_name.encode())


_upper_offset: int = ord("A") - ord("a")


@functools.lru_cache(maxsize=None)
def parse_shortcut(shortcut: str) -> Tuple[Tuple[int, int], Gdk.ModifierType]:
    if Gtk.get_major_version() == 3:
        key, mod = Gtk.accelerator_parse(shortcut)
    else:
        _, key, mod = Gtk.accelerator_parse(shortcut)
    return (key, key + _upper_offset), mod
