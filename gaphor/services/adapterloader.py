from builtins import object

from zope.interface import implementer

from gaphor.interfaces import IService


@implementer(IService)
class AdapterLoader(object):
    """
    Initiate adapters from the gaphor.adapters module.
    """

    def init(self, app):
        pass

    def shutdown(self):
        pass


# vim:sw=4:et:ai
