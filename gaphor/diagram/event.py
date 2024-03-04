class ToolCompleted:
    pass


class DiagramItemPlaced(ToolCompleted):
    def __init__(self, item):
        self.item = item


class DiagramOpened:
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramSelectionChanged:
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items
