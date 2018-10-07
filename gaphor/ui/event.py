from builtins import object

from zope.interface import implementer

from gaphor.ui.interfaces import IDiagramSelectionChange, IDiagramTabChange


@implementer(IDiagramTabChange)
class DiagramTabChange(object):

    def __init__(self, item):
        self.item = item
        self.diagram_tab = item.diagram_tab


@implementer(IDiagramSelectionChange)
class DiagramSelectionChange(object):

    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items


# vim:sw=4:et:ai
