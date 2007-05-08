"""
Interfaces related to the user interface.
"""

from zope import interface


class IDiagramElementReceivedFocus(interface.Interface):
    """A diagram item received focus"""
    diagramItem = interface.Attribute("The diagram item that received focus")
    
    
class IUIComponent(interface.Interface):
    """A user interface component"""
    
    ui_manager = interface.Attribute("The gtk.UIManager, set after construction")
    def construct(self):
        """
        Create and display the UI components (windows).
        """

    #title = interface.Attribute("Title for the window")
    #size = interface.Attribute("initial window size (width, height)")
    #menubar_path = interface.Attribute("UIManager path for menu bar")
    #toolbar_path = interface.Attribute("UIManager path for tool bar")

    #def ui_component(self):
    #    """Create the UI component to be shown in a window."""


class IDetailsPage(IUIComponent):
    """A property page which can display itself in a notebook"""
    

# vim:sw=4:et
