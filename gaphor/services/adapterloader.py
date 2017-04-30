from __future__ import absolute_import

from zope import interface

from gaphor.interfaces import IService


class AdapterLoader(object):
    """
    Initiate adapters from the gaphor.adapters module.
    """

    interface.implements(IService)

    def init(self, app):
        pass

    def shutdown(self):
        pass

# vim:sw=4:et:ai
