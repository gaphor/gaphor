import abc
from zope.interface import implementer


class Service(metaclass=abc.ABCMeta):
    """
    Base interface for all services in Gaphor.
    """

    @abc.abstractmethod
    def init(self, application):
        """
        Initialize the service, this method is called after all services
        are instantiated.
        """

    @abc.abstractmethod
    def shutdown(self):
        """
        Shutdown the services, free resources.
        """


class ActionProvider(metaclass=abc.ABCMeta):
    """
    An action provider is a special service that provides actions
    (see gaphor/action.py) and the accompanying XML for the UI manager.
    """

    menu_xml = "The menu XML"

    action_group = "The accompanying ActionGroup"
