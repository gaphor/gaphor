"""UI related events."""


class ElementOpened:
    def __init__(self, element):
        self.element = element


class DiagramClosed:
    def __init__(self, diagram):
        self.diagram = diagram


class CurrentDiagramChanged:
    def __init__(self, diagram):
        self.diagram = diagram


class ModelSelectionChanged:
    def __init__(self, service, focused_element):
        self.service = service
        self.focused_element = focused_element


class ToolSelected:
    def __init__(self, tool_name):
        self.tool_name = tool_name
