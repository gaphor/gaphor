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
    
class IDiagramElement(interface.Interface):
    """A diagram element"""
    subject = interface.Attribute("The model element connect to this view")    

class INamedItemView(IDiagramElement):
    """A view on an attribute (part of a class, interface etc.)."""
    

class IClassView(INamedItemView):
    """The graphical view on a class."""
    
class IAttributeView(INamedItemView):
    """A view on an attribute (part of a class, interface etc.)."""

