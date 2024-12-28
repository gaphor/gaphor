"""UI related events."""


class ElementFocused:
    def __init__(self, element):
        self.element = element


class ElementOpened:
    def __init__(self, element):
        self.element = element


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
