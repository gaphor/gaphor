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


class IServiceEvent(interface.Interface):
    """
    An event emitted by a service.
    """

    service = interface.Attribute("The service that emits the event")


class ITransaction(interface.Interface):
    """
    The methods each transaction should adhere.
    """

    def commit(self):
        """
        Commit the transaction.
        """

    def rollback(self):
        """
        Roll back the transaction.
        """


class ITransactionEvent(interface.Interface):
    """
    Events related to transaction workflow (begin/commit/rollback) implements
    this interface.
    """


class IActionProvider(interface.Interface):
    """
    An action provider is a special service that provides actions
    (see gaphor/action.py) and the accompanying XML for the UI manager.
    """

    menu_xml = interface.Attribute("The menu XML")

    action_group = interface.Attribute("The accompanying ActionGroup")


class IActionExecutedEvent(interface.Interface):
    """
    An event emitted when an action has been performed.
    """

    name = interface.Attribute("Name of the action performed, if any")

    action = interface.Attribute("The performed action")
