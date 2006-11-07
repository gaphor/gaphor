"""Unittest the storage and parser modules
"""

import os
import unittest
from gaphor import UML
from gaphor import storage
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.diagram import items

class PseudoFile(object):

    def __init__(self):
        self.data = ''

    def write(self, data):
        self.data += data

    def close(self):
        pass


class StorageTestCase(unittest.TestCase):

    def tearDown(self):
        UML.flush()

    def test_save_uml(self):
        """Saving gaphor.UML model elements.
        """
        UML.create(UML.Package)
        UML.create(UML.Diagram)
        UML.create(UML.Comment)
        UML.create(UML.Class)

        out = PseudoFile()
        storage.save(XMLWriter(out))
        out.close()

        assert '<Package ' in out.data
        assert '<Diagram ' in out.data
        assert '<Comment ' in out.data
        assert '<Class ' in out.data
        

    def test_save_item(self):
        """Save a diagranm item too.
        """
        diagram = UML.create(UML.Diagram)
        diagram.create(items.CommentItem, subject=UML.create(UML.Comment))

        out = PseudoFile()
        storage.save(XMLWriter(out))
        out.close()

        assert '<Diagram ' in out.data
        assert '<Comment ' in out.data
        assert '<canvas>' in out.data
        assert ' type="CommentItem" ' in out.data, out.data


    def test_load_uml(self):
        """Test loading of a freshly saved model.
        """
        filename = os.tmpnam()

        UML.create(UML.Package)
        UML.create(UML.Diagram)
        UML.create(UML.Comment)
        UML.create(UML.Class)
 
        fd = open(filename, 'w')
        storage.save(XMLWriter(fd))
        fd.close()

        UML.flush()
        assert not list(UML.select())

        storage.load(filename)

        assert len(UML.lselect()) == 4
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        

    def test_load_uml(self):
        """Test loading of a freshly saved model.
        """
        filename = os.tmpnam()

        UML.create(UML.Package)
        diagram = UML.create(UML.Diagram)
        diagram.create(items.CommentItem, subject=UML.create(UML.Comment))
        diagram.create(items.ClassItem, subject=UML.create(UML.Class))
 
        fd = open(filename, 'w')
        storage.save(XMLWriter(fd))
        fd.close()

        UML.flush()
        assert not list(UML.select())

        storage.load(filename)

        assert len(UML.lselect()) == 4
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        
        # TODO: check load/save of other canvas items.

    def test_load_x_gaphor(self):
        storage.load('x.gaphor')

