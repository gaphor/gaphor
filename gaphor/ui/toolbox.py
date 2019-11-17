"""
Toolbox.
"""


import logging

from gi.repository import Gdk, GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.core import gettext
from gaphor.ui.abc import UIComponent
from gaphor.ui.diagramtoolbox import TOOLBOX_ACTIONS

log = logging.getLogger(__name__)


class Toolbox(UIComponent, ActionProvider):

    TARGET_STRING = 0
    TARGET_TOOLBOX_ACTION = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new(
            "gaphor/toolbox-action", Gtk.TargetFlags.SAME_APP, TARGET_TOOLBOX_ACTION
        ),
    ]

    title = gettext("Toolbox")

    def __init__(self, main_window, properties, toolbox_actions=TOOLBOX_ACTIONS):
        self.main_window = main_window
        self.properties = properties
        self._toolbox = None
        self._toolbox_actions = toolbox_actions

    def open(self):
        widget = self.construct()

        return widget

    def close(self):
        if self._toolbox:
            self._toolbox.destroy()
            self._toolbox = None

    def construct(self):
        def toolbox_button(action_name, icon_name, label, shortcut):
            button = Gtk.ToggleToolButton.new()
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            button.set_icon_widget(icon)
            button.set_action_name("diagram.select-tool")
            button.set_action_target_value(GLib.Variant.new_string(action_name))
            if label:
                if shortcut:
                    a, m = Gtk.accelerator_parse(shortcut)
                    button.set_tooltip_text(
                        f"{label} ({Gtk.accelerator_get_label(a, m)})"
                    )
                else:
                    button.set_tooltip_text(f"{label}")

            # Enable Drag and Drop
            if action_name != "toolbox-pointer":
                inner_button = button.get_children()[0]
                inner_button.drag_source_set(
                    Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
                    self.DND_TARGETS,
                    Gdk.DragAction.COPY | Gdk.DragAction.LINK,
                )
                inner_button.drag_source_set_icon_name(icon_name)
                inner_button.connect(
                    "drag-data-get", self._button_drag_data_get, action_name
                )

            return button

        toolbox = Gtk.ToolPalette.new()
        toolbox.connect("destroy", self._on_toolbox_destroyed)

        collapsed = self.properties.get("toolbox-collapsed", {})

        def on_collapsed(widget, prop, index):
            collapsed[index] = widget.get_property("collapsed")
            self.properties.set("toolbox-collapsed", collapsed)

        for index, (title, items) in enumerate(self._toolbox_actions):
            tool_item_group = Gtk.ToolItemGroup.new(title)
            tool_item_group.set_property("collapsed", collapsed.get(index, False))
            tool_item_group.connect("notify::collapsed", on_collapsed, index)
            for action_name, label, icon_name, shortcut in items:
                button = toolbox_button(action_name, icon_name, label, shortcut)
                tool_item_group.insert(button, -1)
                button.show_all()

            toolbox.add(tool_item_group)
            tool_item_group.show()

        toolbox.show()

        self._toolbox = toolbox

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.add(toolbox)
        scrolled_window.show()
        return scrolled_window

    def _on_toolbox_destroyed(self, widget):
        self._toolbox = None

    def _button_drag_data_get(self, button, context, data, info, time, action_name):
        """The drag-data-get event signal handler.

        The drag-data-get signal is emitted on the drag source when the drop
        site requests the data which is dragged.

        Args:
            button (Gtk.Button): The button that received the signal.
            context (Gdk.DragContext): The drag context.
            data (Gtk.SelectionData): The data to be filled with the dragged
                data.
            info (int): The info that has been registered with the target in
                the Gtk.TargetList
            time (int): The timestamp at which the data was received.

        """
        data.set(type=data.get_target(), format=8, data=action_name.encode())
