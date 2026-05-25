from dataclasses import dataclass


@dataclass
class ToolCompleted:
    cancelled: bool = False


class DiagramItemPlaced(ToolCompleted):
    def __init__(self, item):
        super().__init__(False)
        self.item = item


class DiagramOpened:
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramClosed:
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramSelectionChanged:
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items
