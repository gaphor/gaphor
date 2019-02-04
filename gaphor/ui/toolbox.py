"""
Toolbox.
"""

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor.core import inject


class Toolbox(Gtk.ToolPalette):
    """
    A toolbox is a ToolPalette widget that contains a ToolItems (buttons) that
    are added to a ToolItemGroup. Each group has a label above the buttons.
    When the user clicks on the name the group's content toggles to show or
    hide the buttons.

    The toolbox is generated based on a definition with the form:
    ('name', ('boxAction1', 'boxAction2',...), 'name2', ('BoxActionN',...))

    """

    TARGET_STRING = 0
    TARGET_TOOLBOX_ACTION = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new(
            "gaphor/toolbox-action", Gtk.TargetFlags.SAME_APP, TARGET_TOOLBOX_ACTION
        ),
    ]

    __gsignals__ = {
        "toggled": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (GObject.TYPE_STRING, GObject.TYPE_INT),
        )
    }

    properties = inject("properties")

    def __init__(self, toolboxdef):
        """Create a new Toolbox instance.

        ToolItemGroups and ToolItems are created using the menu_factory and
        based on the toolboxdef definition.

        """
        GObject.GObject.__init__(self)
        self.buttons = []
        self.shortcuts = {}
        self._construct(toolboxdef)

    def toolbox_button(self, action_name, stock_id):
        button = Gtk.ToolButton.new_from_stock(stock_id)
        button.action_name = action_name
        button.set_use_drag_window(True)

        # Enable Drag and Drop
        button.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK,
            self.DND_TARGETS,
            Gdk.DragAction.COPY | Gdk.DragAction.LINK,
        )
        button.drag_source_set_icon_stock(stock_id)
        button.connect("drag-data-get", self._button_drag_data_get)

        return button

    def _construct(self, toolboxdef):
        shortcuts = self.shortcuts
        for title, items in toolboxdef:
            tool_item_group = Gtk.ToolItemGroup.new(title)
            for action_name, label, stock_id, shortcut in items:
                button = self.toolbox_button(action_name, stock_id)
                if label:
                    button.set_tooltip_text("%s (%s)" % (label, shortcut))
                self.buttons.append(button)
                tool_item_group.insert(button, -1)
                button.show()
                shortcuts[shortcut] = action_name
            self.add(tool_item_group)
            tool_item_group.show()

    def _button_drag_data_get(self, button, context, data, info, time):
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
        data.set(type=data.get_target(), format=8, data=button.action_name.encode())


# vim:sw=4:et:ai
