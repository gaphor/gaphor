import abc
from typing import Tuple
from gaphor.abc import Service


class UIComponent(Service):
    """
    A user interface component.
    """

    ui_name: str  # "The UIComponent name, provided by the loader"

    title: str  # "Title of the component"

    size: Tuple[int, int]  # "Size used for floating the component"

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
