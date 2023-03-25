class ToolCompleted:
    pass


class DiagramItemPlaced(ToolCompleted):
    def __init__(self, item):
        self.item = item


class DiagramOpened:
    def __init__(self, diagram):
        self.diagram = diagram
