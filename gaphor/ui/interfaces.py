"""
Interfaces related to the user interface.
"""

from zope import interface


class IDiagram(interface.Interface):
    """
    Show a new diagram tab
    """

    diagram = interface.Attribute("The newly selected Diagram")


class IDiagramPageChange(interface.Interface):
    """
    The selected diagram changes.
    """

    item = interface.Attribute("The newly selected Notebook pane")

    diagram_page = interface.Attribute("The newly selected diagram page")


class IDiagramSelectionChange(interface.Interface):
    """
    The selection of a diagram changed.
    """

    diagram_view = interface.Attribute("The diagram View that emits the event")

    focused_item = interface.Attribute("The diagram item that received focus")

    selected_items = interface.Attribute("All selected items in the diagram")


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
