import abc


class UIComponent(metaclass=abc.ABCMeta):
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
