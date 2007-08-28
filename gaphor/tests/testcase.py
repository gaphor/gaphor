"""
Basic test case for Gaphor tests.

Everything is about services so the TestCase can define it's required
services and start off.
"""

import unittest
from cStringIO import StringIO

from gaphor import UML
from gaphor import storage
from gaphor.application import Application
from gaphor.misc.xmlwriter import XMLWriter

# Increment log level
log.set_log_level(log.WARNING)


class TestCase(unittest.TestCase):
    
    services = ['element_factory']
    
    def setUp(self):
        Application.init(services=self.services)
        self.element_factory = Application.get_service('element_factory')
        self.diagram = self.element_factory.create(UML.Diagram)


    def tearDown(self):
        Application.shutdown()
        self.element_factory.flush()
        self.element_factory.shutdown()
        

    def get_service(self, name):
        return Application.get_service(name)


    def create(self, item_cls, subject_cls):
        """
        Create an item with specified subject.
        """
        subject = self.element_factory.create(subject_cls)
        item = self.diagram.create(item_cls, subject=subject)
        self.diagram.canvas.update()
        return item


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
