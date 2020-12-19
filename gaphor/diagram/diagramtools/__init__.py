"""Tools for handling items on the canvas.

TODO: make tools transactional.
"""

from gaphas.segment import segment_tool
from gaphas.tool import hover_tool, item_tool, rubberband_tool, scroll_tool, zoom_tool

import gaphor.diagram.diagramtools.grayout
from gaphor.diagram.diagramtools.dropzone import drop_zone_tool
from gaphor.diagram.diagramtools.placement import new_item_factory, placement_tool
from gaphor.diagram.diagramtools.textedit import text_edit_tools
from gaphor.diagram.diagramtools.txtool import transactional_tool


def apply_default_tool_set(view, event_manager, rubberband_state):
    """The default tool set."""
    view.remove_all_controllers()
    view.add_controller(hover_tool(view))
    view.add_controller(
        *transactional_tool(
            segment_tool(view), item_tool(view), event_manager=event_manager
        )
    )
    view.add_controller(*text_edit_tools(view))
    view.add_controller(rubberband_tool(view, rubberband_state))
    view.add_controller(scroll_tool(view))
    view.add_controller(zoom_tool(view))


def apply_placement_tool_set(view, item_factory, event_manager, handle_index):
    view.remove_all_controllers()
    view.add_controller(
        *transactional_tool(
            placement_tool(view, item_factory, event_manager, handle_index),
            event_manager=event_manager,
        )
    )
    view.add_controller(drop_zone_tool(view, item_factory.item_class))
    view.add_controller(scroll_tool(view))
    view.add_controller(zoom_tool(view))
