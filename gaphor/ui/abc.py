import abc
from gaphor.abc import Service


class UIComponent(Service):
    """
    A user interface component.
    """

    ui_name = "The UIComponent name, provided by the loader"

    title = "Title of the component"

    size = "Size used for floating the component"

    placement = 'placement. E.g. ("left", "diagrams")'

    @abc.abstractmethod
    def open(self):
        """
        Create and display the UI components (windows).
        """

    @abc.abstractmethod
    def close(self):
        """
        Close the UI component. The component can decide to hide or destroy the UI
        components.
        """

    def shutdown(self):
        """
        Shut down this component. It's not supposed to be opened again.
        """
        self.close()
