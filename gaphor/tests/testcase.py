"""
Basic test case for Gaphor tests.

Everything is about services so the TestCase can define it's required
services and start off.
"""

import unittest
from cStringIO import StringIO
from zope import component

from gaphor import UML
from gaphor.storage import storage
from gaphor.application import Application
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.diagram.interfaces import IConnect

# Increment log level
log.set_log_level(log.WARNING)


class TestCase(unittest.TestCase):
    
    services = ['element_factory', 'adapter_loader']
    
    def setUp(self):
        Application.init(services=self.services)
        self.element_factory = Application.get_service('element_factory')
        assert len(list(self.element_factory.select())) == 0, list(self.element_factory.select())
        self.diagram = self.element_factory.create(UML.Diagram)
        assert len(list(self.element_factory.select())) == 1, list(self.element_factory.select())


    def tearDown(self):
        Application.shutdown()
        

    def get_service(self, name):
        return Application.get_service(name)


    def create(self, item_cls, subject_cls=None, subject=None):
        """
        Create an item with specified subject.
        """
        if subject_cls is not None:
            subject = self.element_factory.create(subject_cls)
        item = self.diagram.create(item_cls, subject=subject)
        self.diagram.canvas.update()
        return item


    def glue(self, line, handle, item, port=None):
        """
        Glue line's handle to an item.
        """
        query = (item, line)
        adapter = component.queryMultiAdapter(query, IConnect)
        return adapter.glue(handle, port)


    def connect(self, line, handle, item, port=None):
        """
        Connect line's handle to an item.
        """
        handle.connected_to = item

        query = (item, line)
        adapter = component.queryMultiAdapter(query, IConnect)
        connected = adapter.connect(handle, port)

        assert handle.connected_to is item

        return connected


    def disconnect(self, line, handle):
        """
        Disconnect line's handle.
        """
        query = (handle.connected_to, line)
        adapter = component.queryMultiAdapter(query, IConnect)
        adapter.disconnect(line.head)

        handle.connected_to = None

        assert handle.connected_to is None


    def kindof(self, cls):
        """
        Find UML metaclass instances using element factory.
        """
        return self.element_factory.lselect(lambda e: e.isKindOf(cls))


    def save(self):
        """
        Save diagram into string.
        """
        f = StringIO()
        storage.save(XMLWriter(f), factory=self.element_factory)
        data = f.getvalue()
        f.close()

        self.element_factory.flush()
        assert not list(self.element_factory.select())
        assert not list(self.element_factory.lselect())
        return data


    def load(self, data):
        """
        Load data from specified string. Update ``TestCase.diagram``
        attribute to hold new loaded diagram.
        """
        f = StringIO(data)
        storage.load(f, factory=self.element_factory)
        f.close()
        
        self.diagram = self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]


main = unittest.main

# vim:sw=4:et:ai
