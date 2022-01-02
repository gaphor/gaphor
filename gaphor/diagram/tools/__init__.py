"""Tools for handling items on a diagram."""
from gaphas.tool import (
    hover_tool,
    item_tool,
    rubberband_tool,
    scroll_tools,
    view_focus_tool,
    zoom_tool,
)
from gi.repository import Gtk

import gaphor.diagram.tools.connector
import gaphor.diagram.tools.grayout
import gaphor.diagram.tools.segment
from gaphor.diagram.tools.dnd import drop_target_tool
from gaphor.diagram.tools.dropzone import drop_zone_tool
from gaphor.diagram.tools.magnet import magnet_tool
from gaphor.diagram.tools.placement import placement_tool
from gaphor.diagram.tools.shortcut import shortcut_tool
from gaphor.diagram.tools.textedit import text_edit_tools
from gaphor.diagram.tools.txtool import transactional_tool


def apply_default_tool_set(view, modeling_language, event_manager, rubberband_state):
    """The default tool set."""
    view.remove_all_controllers()
    view.add_controller(hover_tool(view))
    view.add_controller(
        *transactional_tool(item_tool(view), event_manager=event_manager)
    )
    view.add_controller(*text_edit_tools(view, event_manager))
    view.add_controller(rubberband_tool(view, rubberband_state))
    add_basic_tools(view, modeling_language, event_manager)


def apply_magnet_tool_set(view, modeling_language, event_manager):
    """The default tool set."""
    view.remove_all_controllers()
    view.add_controller(
        *transactional_tool(
            magnet_tool(view, event_manager), event_manager=event_manager
        )
    )
    add_basic_tools(view, modeling_language, event_manager)


def apply_placement_tool_set(
    view, item_factory, modeling_language, event_manager, handle_index
):
    view.remove_all_controllers()
    view.add_controller(view_focus_tool(view))
    view.add_controller(
        *transactional_tool(
            placement_tool(view, item_factory, event_manager, handle_index),
            event_manager=event_manager,
        )
    )
    view.add_controller(drop_zone_tool(view, item_factory.item_class))
    add_basic_tools(view, modeling_language, event_manager)


def add_basic_tools(view, modeling_language, event_manager):
    view.add_controller(*scroll_tools(view))
    view.add_controller(zoom_tool(view))
    view.add_controller(view_focus_tool(view))
    view.add_controller(shortcut_tool(view, modeling_language, event_manager))
    if Gtk.get_major_version() != 3:
        view.add_controller(drop_target_tool(modeling_language, event_manager))
