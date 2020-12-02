"""Tools for handling items on the canvas.

TODO: make tools transactional.
"""

from gaphas.tool import hover_tool, item_tool, rubberband_tool, scroll_tool, zoom_tool

from gaphor.diagram.diagramtools.dropzone import drop_zone_tool
from gaphor.diagram.diagramtools.placement import new_item_factory, placement_tool
from gaphor.diagram.diagramtools.textedit import text_edit_tools


def apply_default_tool_set(view, event_manager, rubberband_state):
    """The default tool set."""
    view.remove_all_controllers()
    view.add_controller(hover_tool(view))
    view.add_controller(item_tool(view))
    view.add_controller(*text_edit_tools(view))
    view.add_controller(rubberband_tool(view, rubberband_state))
    view.add_controller(scroll_tool(view))
    view.add_controller(zoom_tool(view))


def apply_placement_tool_set(view, item_factory, event_manager, handle_index):
    view.remove_all_controllers()
    view.add_controller(placement_tool(view, item_factory, event_manager, handle_index))
    view.add_controller(drop_zone_tool(view, item_factory.item_class))
    view.add_controller(scroll_tool(view))
    view.add_controller(zoom_tool(view))
