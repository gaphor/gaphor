from __future__ import absolute_import
from .interfaces import *

class DiagramTabChange(object):

    interface.implements(IDiagramTabChange)
    
    def __init__(self, item):
        self.item = item
        self.diagram_tab = item.diagram_tab


class DiagramSelectionChange(object):

    interface.implements(IDiagramSelectionChange)
    
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items


# vim:sw=4:et:ai
