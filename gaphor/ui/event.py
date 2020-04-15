"""
UI related events.
"""


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


class ModelingLanguageChanged:
    def __init__(self, modeling_language):
        self.modeling_language = modeling_language


class FileLoaded:
    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename


class FileSaved:
    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename
