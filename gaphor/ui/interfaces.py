"""
Interfaces related to the user interface.
"""

from zope import interface


class IDiagramSelectionChange(interface.Interface):
    """
    The selection of a diagram changed.
    """
    diagram_view = interface.Attribute('The diagram View that emits the event')

    focused_item = interface.Attribute('The diagram item that received focus')

    selected_items = interface.Attribute('All selected items in the diagram')


class IUIComponent(interface.Interface):
    """
    A user interface component
    """
    
    ui_manager = interface.Attribute("The gtk.UIManager, set after construction")
    def construct(self):
        """
        Create and display the UI components (windows).
        """


class IDetailsPage(IUIComponent):
    """
    A property page which can display itself in a notebook
    """
    

# vim:sw=4:et
