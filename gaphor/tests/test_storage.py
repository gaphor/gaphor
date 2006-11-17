"""Unittest the storage and parser modules
"""

import os
import unittest
from gaphor import UML
from gaphor import storage
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.diagram import items

__module__ = 'test_storage'

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
        """
        Test loading of a freshly saved model.
        """
        filename = '%s.gaphor' % __module__

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
        

    def test_load_uml_2(self):
        """
        Test loading of a freshly saved model.
        """
        filename = '%s.gaphor' % __module__

        UML.create(UML.Package)
        diagram = UML.create(UML.Diagram)
        diagram.create(items.CommentItem, subject=UML.create(UML.Comment))
        diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        iface = diagram.create(items.InterfaceItem, subject=UML.create(UML.Interface))
        iface.subject.name = 'Circus'
        iface.matrix.translate(10, 10)

        fd = open(filename, 'w')
        storage.save(XMLWriter(fd))
        fd.close()

        UML.flush()
        assert not list(UML.select())

        storage.load(filename)

        assert len(UML.lselect()) == 5
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = UML.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Interface))) == 1

        c = UML.lselect(lambda e: e.isKindOf(UML.Class))[0]
        assert c.presentation
        assert c.presentation[0].subject is c
        #assert c.presentation[0].subject.name.startwith('Class')

        iface = UML.lselect(lambda e: e.isKindOf(UML.Interface))[0]
        assert iface.name == 'Circus'
        assert len(iface.presentation) == 1
        assert tuple(iface.presentation[0].matrix) == (1, 0, 0, 1, 10, 10), tuple(iface.presentation[0].matrix)
        
        # Check load/save of other canvas items.
        assert len(d.canvas.get_all_items()) == 3
        for item in d.canvas.get_all_items():
            assert item.subject, 'No subject for %s' % item 
        d1 = d.canvas.select(lambda e: isinstance(e, items.ClassItem))[0]
        assert d1
        #print d1, d1.subject


    def test_load_uml_relationships(self):
        """
        Test loading of a freshly saved model with relationship objects.
        """
        filename = '%s.gaphor' % __module__

        UML.create(UML.Package)
        diagram = UML.create(UML.Diagram)
        diagram.create(items.CommentItem, subject=UML.create(UML.Comment))
        c1 = diagram.create(items.ClassItem, subject=UML.create(UML.Class))
        diagram.create(items.AssociationItem)

        fd = open(filename, 'w')
        storage.save(XMLWriter(fd))
        fd.close()

        UML.flush()
        assert not list(UML.select())

        storage.load(filename)

        assert len(UML.lselect()) == 4
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = UML.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        assert len(UML.lselect(lambda e: e.isKindOf(UML.Association))) == 0

        # Check load/save of other canvas items.
        assert len(d.canvas.get_all_items()) == 3
        #for item in d.canvas.get_all_items():
        #    assert item.subject, 'No subject for %s' % item 
        d1 = d.canvas.select(lambda e: isinstance(e, items.ClassItem))[0]
        assert d1
        print d1, d1.subject

# vim:sw=4:et:ai
