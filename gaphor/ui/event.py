"""
UI related events.
"""


class DiagramShow:
    def __init__(self, diagram):
        self.diagram = diagram


class DiagramPageChange:
    def __init__(self, item):
        self.item = item
        self.diagram_page = item.diagram_page


class DiagramSelectionChange:
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items


class WindowClose:
    """
    The user requested the window to be closed.
    """

    def __init__(self, service):
        self.service = service


class FilenameChanged:
    """
    Event class used to send state changes on the Undo Manager.
    """

    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename


class RecentFilesUpdated:
    """
    Event class used to send state changes on the Undo Manager.
    """

    def __init__(self, service, recent_files=[]):
        self.service = service
        self.recent_files = recent_files
