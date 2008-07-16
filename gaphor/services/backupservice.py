"""
"""

import pickle
from zope import interface
from gaphor.application import Application
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject

class MyPickler(pickle.Pickler):

    def save(self, obj):
        #print 'saving obj', obj
        try:
            return pickle.Pickler.save(self, obj)
        except Exception, e:
            print 'Error while pickling', obj, self.dispatch.get(type(obj))
            raise e


class BackupService(object):
    """
    This service makes backups every *x* minutes.
    """

    interface.implements(IService)

    element_factory = inject('element_factory')

    def __init__(self):
        self.tempname = '.backup.gaphor.tmp'


    def init(self, app):
        self._app = app


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
