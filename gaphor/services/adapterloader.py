from zope.interface import implementer

from gaphor.abc import Service
from gaphor.interfaces import IService


@implementer(IService)
class AdapterLoader(Service):
    """
    Initiate adapters from the gaphor.adapters module.
    """

    def init(self, app):
        pass

    def shutdown(self):
        pass
