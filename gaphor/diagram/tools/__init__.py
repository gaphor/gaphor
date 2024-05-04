"""Tools for handling items on a diagram."""

# ruff: noqa: F401

from gaphas.tool import hover_tool, rubberband_tool, view_focus_tool, zoom_tools
from gaphas.tool.scroll import pan_tool

import gaphor.diagram.tools.handlemove
from gaphor.diagram.tools.dnd import drop_target_tool
from gaphor.diagram.tools.dropzone import drop_zone_tool
from gaphor.diagram.tools.itemtool import item_tool
from gaphor.diagram.tools.magnet import magnet_tool
from gaphor.diagram.tools.placement import placement_tool
from gaphor.diagram.tools.shortcut import shortcut_tool
from gaphor.diagram.tools.textedit import text_edit_tools
from gaphor.diagram.tools.txtool import transactional_tool


def apply_default_tool_set(view, modeling_language, event_manager, rubberband_state):
    """The default tool set."""
    view.remove_all_controllers()
    view.add_controller(hover_tool())
    view.add_controller(*text_edit_tools(event_manager))
    view.add_controller(
        *transactional_tool(item_tool(event_manager), event_manager=event_manager)
    )
    view.add_controller(rubberband_tool(rubberband_state))
    add_basic_tools(view, modeling_language, event_manager)


def apply_magnet_tool_set(view, modeling_language, event_manager):
    """The default tool set."""
    view.remove_all_controllers()
    view.add_controller(
        *transactional_tool(magnet_tool(event_manager), event_manager=event_manager)
    )
    add_basic_tools(view, modeling_language, event_manager)


def apply_placement_tool_set(
    view, item_factory, modeling_language, event_manager, handle_index
):
    view.remove_all_controllers()
    view.add_controller(view_focus_tool())
    view.add_controller(
        *transactional_tool(
            placement_tool(item_factory, event_manager, handle_index),
            event_manager=event_manager,
        )
    )
    view.add_controller(
        drop_zone_tool(item_factory.item_class, item_factory.subject_class)
    )
    add_basic_tools(view, modeling_language, event_manager)


def add_basic_tools(view, modeling_language, event_manager):
    for tool in zoom_tools():
        view.add_controller(tool)
    view.add_controller(pan_tool())
    view.add_controller(view_focus_tool())
    view.add_controller(shortcut_tool(event_manager))
    view.add_controller(drop_target_tool(modeling_language, event_manager))
