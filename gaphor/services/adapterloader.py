
from __future__ import absolute_import
from zope import interface
from gaphor.interfaces import IService


class AdapterLoader(object):
    """
    Initiate adapters from the gaphor.adapters module.
    """

    interface.implements(IService)

    def init(self, app):
        import gaphor.adapters
        import gaphor.adapters.connectors
        import gaphor.adapters.editors
        import gaphor.adapters.grouping
        import gaphor.adapters.propertypages
        import gaphor.adapters.states

    def shutdown(self):
        pass


# vim:sw=4:et:ai
