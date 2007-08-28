"""
Basic test case for Gaphor tests.

Everything is about services so the TestCase can define it's required
services and start off.
"""

import unittest
from gaphor.application import Application
from gaphor import UML

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


main = unittest.main

# vim:sw=4:et:ai
