"""
"""

import pickle

from zope.interface import implementer

from gaphor.UML import Element
from gaphor.core import inject
from gaphor.interfaces import IService
from gaphor.misc.latepickle import LatePickler


class MyPickler(LatePickler):
    """
    Customize the pickler to only delay instantiations of Element objects.
    """

    def delay(self, obj):
        return isinstance(obj, Element)


@implementer(IService)
class BackupService(object):
    """
    This service makes backups every *x* minutes.
    """

    element_factory = inject('element_factory')

    def __init__(self):
        self.tempname = '.backup.gaphor.tmp'


    def init(self, app):
        pass


    def shutdown(self):
        pass


    def backup(self):
        f = open(self.tempname, 'w')
        try:
            pickler = MyPickler(f)
            pickler.dump(self.element_factory.lselect())
        finally:
            f.close()


    def restore(self):
        f = open(self.tempname, 'r')
        try:
            elements = pickle.Unpickler(f).load()
        finally:
            f.close()
        self.element_factory.flush()
        map(self.element_factory.bind, elements)


# vim: sw=4:et:ai
