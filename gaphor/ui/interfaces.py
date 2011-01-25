"""
Interfaces related to the user interface.
"""

from zope import interface


class IDiagramTabChange(interface.Interface):
    """
    The selected diagram changes.
    """
    item = interface.Attribute('The newly selected DockItem')

    diagram_tab = interface.Attribute('The newly selected diagram tab')

class IDiagramSelectionChange(interface.Interface):
    """
    The selection of a diagram changed.
    """
    diagram_view = interface.Attribute('The diagram View that emits the event')

    focused_item = interface.Attribute('The diagram item that received focus')

    selected_items = interface.Attribute('All selected items in the diagram')


class IUIComponent(interface.Interface):
    """
    A user interface component.
    """
    
    def open(self):
        """
        Create and display the UI components (windows).
        """

    def close(self):
        """
        Close the UI component. The component can decide to hide or destroy the UI
        components.
        """


class IPropertyPage(interface.Interface):
    """
    A property page which can display itself in a notebook
    """
    
    order = interface.Attribute('Order number, used for ordered display')

    def construct(self):
        """
        Create the page (gtk.Widget) that belongs to the Property page.

        Returns the page's toplevel widget (gtk.Widget).
        """

    def destroy(self):
        """
        Destroy the page and clean up signal handlers and stuff.
        """


# vim:sw=4:et:ai
