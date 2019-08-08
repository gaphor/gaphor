"""
Toolbox.
"""

import logging

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor.core import _, event_handler, toggle_action, build_action_group
from gaphor.abc import ActionProvider
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramPageChange
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

    title = _("Toolbox")

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator/>
            <menuitem action="reset-tool-after-create" />
            <separator/>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(
        self, event_manager, main_window, properties, toolbox_actions=TOOLBOX_ACTIONS
    ):
        self.event_manager = event_manager
        self.main_window = main_window
        self.properties = properties
        self._toolbox = None
        self._toolbox_actions = toolbox_actions
        self.action_group = build_action_group(self)
        self.action_group.get_action("reset-tool-after-create").set_active(
            self.properties.get("reset-tool-after-create", True)
        )
        self.buttons = []
        self.shortcuts = {}

    def open(self):
        widget = self.construct()
        self.main_window.window.connect_after(
            "key-press-event", self._on_key_press_event
        )
        self.event_manager.subscribe(self._on_diagram_page_change)
        return widget

    def close(self):
        if self._toolbox:
            self._toolbox.destroy()
            self._toolbox = None
        self.event_manager.unsubscribe(self._on_diagram_page_change)

    def construct(self):
        def toolbox_button(action_name, icon_name, label, shortcut):
            button = Gtk.ToggleToolButton.new()
            icon = Gtk.Image.new_from_icon_name(icon_name, 48)
            button.set_icon_widget(icon)
            button.action_name = action_name
            if label:
                button.set_tooltip_text(f"{label} ({shortcut})")

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

        for title, items in self._toolbox_actions:
            tool_item_group = Gtk.ToolItemGroup.new(title)
            for action_name, label, stock_id, shortcut in items:
                button = toolbox_button(action_name, stock_id, label, shortcut)
                tool_item_group.insert(button, -1)
                button.show_all()
                self.buttons.append(button)
                self.shortcuts[shortcut] = action_name
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

    def _on_key_press_event(self, view, event):
        """
        Grab top level window events and select the appropriate tool based on the event.
        """
        if event.get_state() & Gdk.ModifierType.SHIFT_MASK or (
            event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK
        ):
            keyval = Gdk.keyval_name(event.keyval)
            self.set_active_tool(shortcut=keyval)

    def _on_toolbox_destroyed(self, widget):
        self._toolbox = None

    @toggle_action(name="reset-tool-after-create", label=_("_Reset tool"), active=False)
    def reset_tool_after_create(self, active):
        self.properties.set("reset-tool-after-create", active)

    @event_handler(DiagramPageChange)
    def _on_diagram_page_change(self, event):
        self.update_toolbox(event.diagram_page.toolbox.action_group)

    def update_toolbox(self, action_group):
        """
        Update the buttons in the toolbox. Each button should be connected
        by an action. Each button is assigned a special _action_name_
        attribute that can be used to fetch the action from the ui manager.
        """
        if not self._toolbox:
            return

        for button in self.buttons:
            action_name = button.action_name
            action = action_group.get_action(action_name)
            if action:
                button.set_related_action(action)

    def set_active_tool(self, action_name=None, shortcut=None):
        """
        Set the tool based on the name of the action
        """
        # HACK:
        toolbox = self._toolbox
        if shortcut and toolbox:
            action_name = self.shortcuts.get(shortcut)
            log.debug(f"Action for shortcut {shortcut}: {action_name}")
            if not action_name:
                return

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
