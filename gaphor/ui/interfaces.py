"""
Interfaces related to the user interface.
"""

from zope import interface


class IUIComponent(interface.Interface):
    """
    A user interface component.
    """

    ui_name = interface.Attribute("The UIComponent name, provided by the loader")

    title = interface.Attribute("Title of the component")

    size = interface.Attribute("Size used for floating the component")

    placement = interface.Attribute('placement. E.g. ("left", "diagrams")')

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

    order = interface.Attribute("Order number, used for ordered display")

    def construct(self):
        """
        Create the page (Gtk.Widget) that belongs to the Property page.

        Returns the page's toplevel widget (Gtk.Widget).
        """

    def destroy(self):
        """
        Destroy the page and clean up signal handlers and stuff.
        """
