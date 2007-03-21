"""
Interfaces related to the user interface.
"""

from zope import interface


class IDiagramElementReceivedFocus(interface.Interface):
    """A diagram item received focus"""
    diagramItem = interface.Attribute("The diagram item that received focus")
    
    
class IUIComponent(interface.Interface):
    """A user interface component"""
    
class IDetailsPage(IUIComponent):
    """A property page which can display itself in a notebook"""
    

# vim:sw=4:et
