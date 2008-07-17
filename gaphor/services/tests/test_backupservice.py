"""
Test the backup service.
"""

import unittest
from StringIO import StringIO
from gaphor.storage import storage
from gaphor.application import Application
from gaphor.misc.xmlwriter import XMLWriter

class BackupServiceTestCase(unittest.TestCase):

    services = ['element_factory', 'backup_service']

    def setUp(self):
        Application.init(services=self.services)
        self.element_factory = Application.get_service('element_factory')
        self.backup_service = Application.get_service('backup_service')

    def tearDown(self):
        Application.shutdown()
        
    def save_and_load(self, filename):
        factory = self.element_factory

        f = open(filename, 'r')
        storage.load(f, factory=self.element_factory)
        f.close()
        
        self.backup_service.backup()
        
        elements = map(factory.lookup, factory.keys())

        orig = StringIO()
        storage.save(XMLWriter(orig), factory=self.element_factory)

        self.backup_service.restore()

        restored = map(factory.lookup, factory.keys())

        assert len(elements) == len(restored)
        assert elements != restored

        copy = StringIO()
        storage.save(XMLWriter(copy), factory=self.element_factory)

        orig = orig.getvalue()
        copy = copy.getvalue()
        assert len(orig) == len(copy)
        #assert orig == copy, orig + ' != ' + copy


    def test_simple(self):
        self.save_and_load('test-diagrams/simple-items.gaphor')


    def test_namespace(self):
        self.save_and_load('test-diagrams/namespace.gaphor')

    def test_association(self):
        self.save_and_load('test-diagrams/association.gaphor')

    def test_interactions(self):
        self.save_and_load('test-diagrams/interactions.gaphor')

    def test_bicycle(self):
        self.save_and_load('test-diagrams/bicycle.gaphor')

    def test_line_align(self):
        self.save_and_load('test-diagrams/line-align.gaphor')

#    def test_gaphas_canvas(self):
#        self.save_and_load('../gaphas/gaphor-canvas.gaphor')

    def test_stereotype(self):
        self.save_and_load('test-diagrams/stereotype.gaphor')


# vim: sw=4:et:ai
