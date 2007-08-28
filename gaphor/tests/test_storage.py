"""
Unittest the storage and parser modules
"""

import os
from testcase import TestCase
from gaphor import UML
from gaphor.UML.elementfactory import ElementFactory
from gaphor.application import Application
from gaphor import storage
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect
from zope import component
from cStringIO import StringIO

__module__ = 'test_storage'

class PseudoFile(object):

    def __init__(self):
        self.data = ''

    def write(self, data):
        self.data += data

    def close(self):
        pass


class StorageTestCase(TestCase):

    services = TestCase.services + ['adapter_loader']

    def test_save_uml(self):
        """Saving gaphor.UML model elements.
        """
        self.element_factory.create(UML.Package)
        self.element_factory.create(UML.Diagram)
        self.element_factory.create(UML.Comment)
        self.element_factory.create(UML.Class)

        out = PseudoFile()
        storage.save(XMLWriter(out), factory=self.element_factory)
        out.close()

        assert '<Package ' in out.data
        assert '<Diagram ' in out.data
        assert '<Comment ' in out.data
        assert '<Class ' in out.data
        

    def test_save_item(self):
        """Save a diagranm item too.
        """
        diagram = self.element_factory.create(UML.Diagram)
        diagram.create(items.CommentItem, subject=self.element_factory.create(UML.Comment))

        out = PseudoFile()
        storage.save(XMLWriter(out), factory=self.element_factory)
        out.close()

        assert '<Diagram ' in out.data
        assert '<Comment ' in out.data
        assert '<canvas>' in out.data
        assert ' type="CommentItem" ' in out.data, out.data


    def test_load_uml(self):
        """
        Test loading of a freshly saved model.
        """
        self.element_factory.create(UML.Package)
        # diagram is created in TestCase.setUp
        #self.element_factory.create(UML.Diagram)
        self.element_factory.create(UML.Comment)
        self.element_factory.create(UML.Class)
 
        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 4
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        # diagram is created in TestCase.setUp
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        

    def test_load_uml_2(self):
        """
        Test loading of a freshly saved model.
        """
        self.element_factory.create(UML.Package)
        self.create(items.CommentItem, UML.Comment)
        self.create(items.ClassItem, UML.Class)
        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.subject.name = 'Circus'
        iface.matrix.translate(10, 10)

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 5
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Interface))) == 1

        c = self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))[0]
        assert c.presentation
        assert c.presentation[0].subject is c
        #assert c.presentation[0].subject.name.startwith('Class')

        iface = self.element_factory.lselect(lambda e: e.isKindOf(UML.Interface))[0]
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
        self.element_factory.create(UML.Package)
        self.create(items.CommentItem, UML.Comment)
        c1 = self.create(items.ClassItem, UML.Class)

        a = self.diagram.create(items.AssociationItem)
        a.handles()[0].pos = (10, 20)
        a.handles()[1].pos = (50, 60)
        assert 10 == a.handles()[0].x, a.handles()[0].pos
        assert a.handles()[0].y == 20, a.handles()[0].pos
        assert a.handles()[1].pos == (50, 60), a.handles()[1].pos

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 4
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Association))) == 0

        # Check load/save of other canvas items.
        assert len(d.canvas.get_all_items()) == 3
        for item in d.canvas.get_all_items():
            if isinstance(item, items.AssociationItem):
                aa = item
        assert aa
        assert map(float, aa.handles()[0].pos) == [0, 0], aa.handles()[0].pos
        assert map(float, aa.handles()[1].pos) == [40, 40], aa.handles()[1].pos
        d1 = d.canvas.select(lambda e: isinstance(e, items.ClassItem))[0]
        assert d1
        #print d1, d1.subject

    def test_connection(self):
        """
        Test connection loading of an association and two classes.
        (Should count for all line-like objects alike if this works).
        """
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)
        c2.matrix.translate(200, 200)
        self.diagram.canvas.update_matrix(c2)
        assert tuple(self.diagram.canvas.get_matrix_i2c(c2)) == (1, 0, 0, 1, 200, 200)

        a = self.diagram.create(items.AssociationItem)

        # Provide our element factory as Utility, since the connect adapters
        # depend on it.
        from gaphor.interfaces import IService
        component.provideUtility(self.element_factory, IService, 'element_factory')

        adapter = component.queryMultiAdapter((c1, a), IConnect)
        assert adapter
        h = a.head
        adapter.connect(h)
        head_pos = h.pos

        adapter = component.queryMultiAdapter((c2, a), IConnect)
        assert adapter
        h = a.tail
        adapter.connect(h)
        tail_pos = h.pos

        self.diagram.canvas.update_now()

        assert a.head.y == 0, a.head.pos
        assert a.tail.x == 10, a.tail.pos
        #assert a.tail.y == 200, a.tail.pos
        assert a.subject

        fd = StringIO()
        storage.save(XMLWriter(fd), factory=self.element_factory)
        data = fd.getvalue()
        fd.close()

        old_a_subject_id = a.subject.id

        self.element_factory.flush()
        assert not list(self.element_factory.select())
        fd = StringIO(data)
        storage.load(fd, factory=self.element_factory)
        fd.close()

        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        a = d.canvas.select(lambda e: isinstance(e, items.AssociationItem))[0]
        assert a.subject
        assert old_a_subject_id == a.subject.id
        assert a.head.connected_to
        assert a.tail.connected_to
        assert not a.head.connected_to is a.tail.connected_to
        #assert a.head_end._name


# vim:sw=4:et:ai
