
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
        #reload(gaphor.adapters.connectors)
        import gaphor.adapters.editors
        #reload(gaphor.adapters.editors)
        import gaphor.adapters.grouping
        #reload(gaphor.adapters.grouping)
        import gaphor.adapters.propertypages
        #reload(gaphor.adapters.propertypages)

    def shutdown(self):
        pass


# vim:sw=4:et:ai
