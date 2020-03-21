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


class ProfileSelectionChanged:
    def __init__(self, profile):
        self.profile = profile


class WindowClosed:
    """
    The user requested the window to be closed.
    """

    def __init__(self, service):
        self.service = service


class FileLoaded:
    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename


class FileSaved:
    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename
