
import pkg_resources
from zope import interface
from gaphor.interfaces import IService


class AdapterLoader(object):
    """
    Initiate adapters from the gaphor.adapters module.
    """

    interface.implements(IService)

    def init(self, app):
        self._app = app
        import gaphor.adapters.connectors
        import gaphor.adapters.editors
        import gaphor.adapters.propertypages
        
    def shutdown(self):
        pass


# vim:sw=4:et:ai
