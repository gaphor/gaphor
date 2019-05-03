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
