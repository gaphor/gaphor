"""UI related events."""


class DiagramOpened:
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramClosed:
    def __init__(self, diagram):
        self.diagram = diagram


class CurrentDiagramChanged:
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramSelectionChanged:
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items


class ToolSelected:
    def __init__(self, tool_name):
        self.tool_name = tool_name
