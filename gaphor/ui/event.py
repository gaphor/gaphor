from zope import interface
from interfaces import *

class DiagramItemFocused(object):
    interface.implements(IDiagramElementReceivedFocus)
    
    def __init__(self, diagramItem):
        self.diagramItem = diagramItem
