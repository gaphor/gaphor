from zope import interface
from zope import component
class IGaphorAction(interface.Interface):
    """Action interface for use in Gaphor"""

class IMenuAction(interface.Interface):
    """An interface to hook up items to."""
    

class TestAdapter(object):
    def __init__(self, context):
        self.context = context

#component.provideAdapter(
    #factory=TestAdapter,
    #adapts=[IGaphorAction],
    #provides=IZopeMenu,
    #name="Test adapter name")

#class TestAdapter2(object):
    #def __init__(self, context):
        #self.context = context

#component.provideAdapter(
    #factory=TestAdapter2,
    #adapts=[IGaphorAction],
    #provides=IZopeMenu,
    #name="Test adapter 2 name")

#class TestAction(object):
    #interface.implements(IGaphorAction)
    
class IDiagramElementReceivedFocus(interface.Interface):
    """A diagram item received focus"""
    diagramItem = interface.Attribute("The diagram item that received focus")
    
    
class IWidget(interface.Interface):
    """A GTK widget"""
    
class IDetailsPage(IWidget):
    """A property page which can display itself in a notebook"""
    
###
# Depricated
#
from diagram.interfaces import IDiagramItem as IDiagramElement
from diagram.interfaces import INamedItem as INamedItemView
from diagram.interfaces import IClassItem as IClassView
from diagram.interfaces import IAttributeItem as IAttributeView

