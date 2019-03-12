"""
Unittest the storage and parser modules
"""

import io
import os
import os.path
import re
from io import StringIO

import pkg_resources

from gaphor import UML
from gaphor.diagram import items
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.storage import storage
from gaphor.tests.testcase import TestCase


class PseudoFile(object):
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def close(self):
        pass


class StorageTestCase(TestCase):
    def test_version_check(self):
        from gaphor.storage.storage import version_lower_than

        self.assertTrue(version_lower_than("0.3.0", (0, 15, 0)))
        self.assertTrue(version_lower_than("0", (0, 15, 0)))
        self.assertTrue(version_lower_than("0.14", (0, 15, 0)))
        self.assertTrue(version_lower_than("0.14.1111", (0, 15, 0)))
        self.assertFalse(version_lower_than("0.15.0", (0, 15, 0)))
        self.assertFalse(version_lower_than("1.33.0", (0, 15, 0)))
        self.assertTrue(version_lower_than("0.15.0.b123", (0, 15, 0)))
        self.assertTrue(version_lower_than("0.14.0.b1", (0, 15, 0)))
        self.assertTrue(version_lower_than("0.15.b1", (0, 15, 0)))
        self.assertFalse(version_lower_than("0.16.b1", (0, 15, 0)))
        self.assertFalse(version_lower_than("0.15.0.b2", (0, 14, 99)))

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

        assert "<Package " in out.data
        assert "<Diagram " in out.data
        assert "<Comment " in out.data
        assert "<Class " in out.data

    def test_save_item(self):
        """Save a diagranm item too.
        """
        diagram = self.element_factory.create(UML.Diagram)
        diagram.create(
            items.CommentItem, subject=self.element_factory.create(UML.Comment)
        )

        out = PseudoFile()
        storage.save(XMLWriter(out), factory=self.element_factory)
        out.close()

        assert "<Diagram " in out.data
        assert "<Comment " in out.data
        assert "<canvas>" in out.data
        assert ' type="CommentItem"' in out.data, out.data

    def test_load_uml(self):
        """
        Test loading of a freshly saved model.
        """
        self.element_factory.create(UML.Package)
        # diagram is created in TestCase.setUp
        # self.element_factory.create(UML.Diagram)
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
        iface.subject.name = "Circus"
        iface.matrix.translate(10, 10)

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 5
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        assert (
            len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Interface))) == 1
        )

        c = self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))[0]
        assert c.presentation
        assert c.presentation[0].subject is c
        # assert c.presentation[0].subject.name.startwith('Class')

        iface = self.element_factory.lselect(lambda e: e.isKindOf(UML.Interface))[0]
        assert iface.name == "Circus"
        assert len(iface.presentation) == 1
        assert tuple(iface.presentation[0].matrix) == (1, 0, 0, 1, 10, 10), tuple(
            iface.presentation[0].matrix
        )

        # Check load/save of other canvas items.
        assert len(d.canvas.get_all_items()) == 3
        for item in d.canvas.get_all_items():
            assert item.subject, "No subject for %s" % item
        d1 = d.canvas.select(lambda e: isinstance(e, items.ClassItem))[0]
        assert d1

    def test_load_with_whitespace_name(self):
        difficult_name = "    with space before and after  "
        diagram = self.element_factory.lselect()[0]
        diagram.name = difficult_name
        data = self.save()
        self.load(data)
        elements = self.element_factory.lselect()
        assert len(elements) == 1, elements
        assert elements[0].name == difficult_name, elements[0].name

    def test_load_uml_metamodel(self):
        """
        Test if the meta model can be loaded.
        """

        dist = pkg_resources.get_distribution("gaphor")
        path = os.path.join(dist.location, "gaphor/UML/uml2.gaphor")

        with io.open(path) as ifile:
            storage.load(ifile, factory=self.element_factory)

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
        assert 10 == a.handles()[0].pos.x, a.handles()[0].pos
        assert a.handles()[0].pos.y == 20, a.handles()[0].pos
        assert tuple(a.handles()[1].pos) == (50, 60), a.handles()[1].pos

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 4
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Package))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Class))) == 1
        assert (
            len(self.element_factory.lselect(lambda e: e.isKindOf(UML.Association)))
            == 0
        )

        # Check load/save of other canvas items.
        assert len(d.canvas.get_all_items()) == 3
        for item in d.canvas.get_all_items():
            if isinstance(item, items.AssociationItem):
                aa = item
        assert aa
        assert list(map(float, aa.handles()[0].pos)) == [0, 0], aa.handles()[0].pos
        assert list(map(float, aa.handles()[1].pos)) == [40, 40], aa.handles()[1].pos
        d1 = d.canvas.select(lambda e: isinstance(e, items.ClassItem))[0]
        assert d1

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

        a = self.create(items.AssociationItem)

        self.connect(a, a.head, c1)
        head_pos = a.head.pos

        self.connect(a, a.tail, c2)
        tail_pos = a.tail.pos

        self.diagram.canvas.update_now()

        assert a.head.pos.y == 0, a.head.pos
        assert a.tail.pos.x == 10, a.tail.pos
        # assert a.tail.y == 200, a.tail.pos
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

        diagrams = list(self.kindof(UML.Diagram))
        self.assertEqual(1, len(diagrams))
        d = diagrams[0]
        a = d.canvas.select(lambda e: isinstance(e, items.AssociationItem))[0]
        self.assertTrue(a.subject is not None)
        self.assertEqual(old_a_subject_id, a.subject.id)
        cinfo_head = a.canvas.get_connection(a.head)
        self.assertTrue(cinfo_head.connected is not None)
        cinfo_tail = a.canvas.get_connection(a.tail)
        self.assertTrue(cinfo_tail.connected is not None)
        self.assertTrue(not cinfo_head.connected is cinfo_tail.connected)
        # assert a.head_end._name

    def test_load_save(self):

        """Test loading and saving models"""

        dist = pkg_resources.get_distribution("gaphor")
        path = os.path.join(dist.location, "test-diagrams/simple-items.gaphor")

        with io.open(path, "r") as ifile:
            storage.load(ifile, factory=self.element_factory)

        pf = PseudoFile()

        storage.save(XMLWriter(pf), factory=self.element_factory)

        with io.open(path, "r") as ifile:

            orig = ifile.read()

        copy = pf.data

        with io.open("tmp.gaphor", "w") as ofile:

            ofile.write(copy)

        expr = re.compile('gaphor-version="[^"]*"')
        orig = expr.sub("%VER%", orig)
        copy = expr.sub("%VER%", copy)

        self.maxDiff = None
        self.assertEqual(copy, orig, "Saved model does not match copy")

    def test_loading_an_old_version(self):

        """Test loading and saving models"""

        dist = pkg_resources.get_distribution("gaphor")
        path = os.path.join(dist.location, "test-diagrams/old-gaphor-version.gaphor")

        def load_old_model():
            with io.open(path, "r") as ifile:
                storage.load(ifile, factory=self.element_factory)

        self.assertRaises(ValueError, load_old_model)
