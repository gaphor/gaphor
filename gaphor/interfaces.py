"""
Top level interface definitions for Gaphor.
"""

from zope import interface


class IService(interface.Interface):
    """
    Base interface for all services in Gaphor.
    """

    def init(self, application):
        """
        Initialize the service, this method is called after all services
        are instantiated.
        """

    def shutdown(self):
        """
        Shutdown the services, free resources.
        """


class IActionProvider(interface.Interface):
    """
    An action provider is a special service that provides actions
    (see gaphor/action.py) and the accompanying XML for the UI manager.
    """

    menu_xml = interface.Attribute("The menu XML")

    action_group = interface.Attribute("The accompanying ActionGroup")
