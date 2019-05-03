"""
UI related events.
"""


class DiagramShow(object):
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramPageChange(object):
    def __init__(self, item):
        self.item = item
        self.diagram_page = item.diagram_page


class DiagramSelectionChange(object):
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items
