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


class IServiceEvent(interface.Interface):
    """
    An event emitted by a service.
    """
    service = interface.Attribute("The service that emits the event")


# vim:sw=4:et
