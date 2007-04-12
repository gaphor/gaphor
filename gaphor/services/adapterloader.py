
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
        #for ep in pkg_resources.iter_entry_points('gaphor.adapters'):
            #log.debug('Loading adapters for %s' % ep.name)
            #ep.load()
        
    def shutdown(self):
        pass


# vim:sw=4:et:ai
