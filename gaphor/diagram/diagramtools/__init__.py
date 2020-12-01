"""Tools for handling items on the canvas.

Although Gaphas has quite a few useful tools, some tools need to be extended:
 - PlacementTool: should perform undo
 - HandleTool: should support adapter based connection protocol
 - TextEditTool: should support adapter based edit protocol
"""

from gaphas.tool import hover_tool, item_tool, rubberband_tool

from gaphor.diagram.diagramtools.dropzone import DropZoneMove
from gaphor.diagram.diagramtools.placement import Connector, PlacementTool
from gaphor.diagram.diagramtools.textedit import text_edit_tools


def apply_default_tool_set(view, event_manager, rubberband_state):
    """The default tool set."""
    view.add_controller(hover_tool(view))
    view.add_controller(item_tool(view))
    view.add_controller(*text_edit_tools(view))
    view.add_controller(rubberband_tool(view, rubberband_state))
