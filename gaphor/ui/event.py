from zope import interface
from interfaces import *

class DiagramSelectionChange(object):

    interface.implements(IDiagramSelectionChange)
    
    def __init__(self, diagram_view, focused_item, selected_items):
        self.diagram_view = diagram_view
        self.focused_item = focused_item
        self.selected_items = selected_items


# vim:sw=4:et:ai
