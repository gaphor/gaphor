"""
Interfaces related to the user interface.
"""

from zope import interface


class _PropertyPages:
    def __init__(self):
        self.pages = []

    def register(self, subject_type):
        def reg(func):
            self.pages.append((subject_type, func))
            return func

        return reg

    def __call__(self, subject):
        for subject_type, func in self.pages:
            if isinstance(subject, subject_type):
                yield func(subject)


PropertyPages = _PropertyPages()


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
