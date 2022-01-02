class ToolCompleted:
    pass


class DiagramItemPlaced(ToolCompleted):
    def __init__(self, item):
        self.item = item
