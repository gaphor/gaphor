#!/usr/bin/env python

# Copyright (C) 2007-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Unittest the storage and parser modules
"""

from __future__ import absolute_import
import os
import re
import os.path
import pkg_resources
from gaphor.tests.testcase import TestCase
from gaphor.UML import uml2
from gaphor.storage import storage
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.diagram import items
from cStringIO import StringIO
from six.moves import map


# __module__ = 'test_storage'

class PseudoFile(object):
    def __init__(self):
        self.data = ''

    def write(self, data):
        self.data += data

    def close(self):
        pass


class StorageTestCase(TestCase):
    def test_version_check(self):
        from gaphor.storage.storage import version_lower_than
        self.assertTrue(version_lower_than('0.3.0', (0, 15, 0)))
        self.assertTrue(version_lower_than('0', (0, 15, 0)))
        self.assertTrue(version_lower_than('0.14', (0, 15, 0)))
        self.assertTrue(version_lower_than('0.14.1111', (0, 15, 0)))
        self.assertFalse(version_lower_than('0.15.0', (0, 15, 0)))
        self.assertFalse(version_lower_than('1.33.0', (0, 15, 0)))
        self.assertTrue(version_lower_than('0.15.0.b123', (0, 15, 0)))
        self.assertTrue(version_lower_than('0.14.0.b1', (0, 15, 0)))
        self.assertTrue(version_lower_than('0.15.b1', (0, 15, 0)))
        self.assertFalse(version_lower_than('0.16.b1', (0, 15, 0)))
        self.assertFalse(version_lower_than('0.15.0.b2', (0, 14, 99)))

    def test_save_uml(self):
        """Saving gaphor.uml2 model elements.
        """
        self.element_factory.create(uml2.Package)
        self.element_factory.create(uml2.Diagram)
        self.element_factory.create(uml2.Comment)
        self.element_factory.create(uml2.Class)

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
        diagram = self.element_factory.create(uml2.Diagram)
        diagram.create(items.CommentItem, subject=self.element_factory.create(uml2.Comment))

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
        self.element_factory.create(uml2.Package)
        # diagram is created in TestCase.setUp
        # self.element_factory.create(uml2.Diagram)
        self.element_factory.create(uml2.Comment)
        self.element_factory.create(uml2.Class)

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 4
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Package))) == 1
        # diagram is created in TestCase.setUp
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Class))) == 1

    def test_load_uml_2(self):
        """
        Test loading of a freshly saved model.
        """
        self.element_factory.create(uml2.Package)
        self.create(items.CommentItem, uml2.Comment)
        self.create(items.ClassItem, uml2.Class)
        iface = self.create(items.InterfaceItem, uml2.Interface)
        iface.subject.name = 'Circus'
        iface.matrix.translate(10, 10)

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 5
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Package))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))[0]
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Class))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Interface))) == 1

        c = self.element_factory.lselect(lambda e: e.isKindOf(uml2.Class))[0]
        assert c.presentation
        assert c.presentation[0].subject is c
        # assert c.presentation[0].subject.name.startwith('Class')

        iface = self.element_factory.lselect(lambda e: e.isKindOf(uml2.Interface))[0]
        assert iface.name == 'Circus'
        assert len(iface.presentation) == 1
        assert tuple(iface.presentation[0].matrix) == (1, 0, 0, 1, 10, 10), tuple(iface.presentation[0].matrix)

        # Check load/save of other canvas items.
        assert len(d.canvas.get_all_items()) == 3
        for item in d.canvas.get_all_items():
            assert item.subject, 'No subject for %s' % item
        d1 = d.canvas.select(lambda e: isinstance(e, items.ClassItem))[0]
        assert d1
        # print d1, d1.subject

    def test_load_with_whitespace_name(self):
        difficult_name = '    with space before and after  '
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

        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'gaphor/UML/uml2.gaphor')

        with open(path) as ifile:
            storage.load(ifile, factory=self.element_factory)

    def test_load_uml_relationships(self):
        """
        Test loading of a freshly saved model with relationship objects.
        """
        self.element_factory.create(uml2.Package)
        self.create(items.CommentItem, uml2.Comment)
        c1 = self.create(items.ClassItem, uml2.Class)

        a = self.diagram.create(items.AssociationItem)
        a.handles()[0].pos = (10, 20)
        a.handles()[1].pos = (50, 60)
        assert 10 == a.handles()[0].pos.x, a.handles()[0].pos
        assert a.handles()[0].pos.y == 20, a.handles()[0].pos
        assert tuple(a.handles()[1].pos) == (50, 60), a.handles()[1].pos

        data = self.save()
        self.load(data)

        assert len(self.element_factory.lselect()) == 4
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Package))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))) == 1
        d = self.element_factory.lselect(lambda e: e.isKindOf(uml2.Diagram))[0]
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Comment))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Class))) == 1
        assert len(self.element_factory.lselect(lambda e: e.isKindOf(uml2.Association))) == 0

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
        # print d1, d1.subject

    def test_connection(self):
        """
        Test connection loading of an association and two classes.
        (Should count for all line-like objects alike if this works).
        """
        c1 = self.create(items.ClassItem, uml2.Class)
        c2 = self.create(items.ClassItem, uml2.Class)
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

        diagrams = list(self.kindof(uml2.Diagram))
        self.assertEquals(1, len(diagrams))
        d = diagrams[0]
        a = d.canvas.select(lambda e: isinstance(e, items.AssociationItem))[0]
        self.assertTrue(a.subject is not None)
        self.assertEquals(old_a_subject_id, a.subject.id)
        cinfo_head = a.canvas.get_connection(a.head)
        self.assertTrue(cinfo_head.connected is not None)
        cinfo_tail = a.canvas.get_connection(a.tail)
        self.assertTrue(cinfo_tail.connected is not None)
        self.assertTrue(cinfo_head.connected is not cinfo_tail.connected)
        # assert a.head_end._name

    def test_load_save(self):

        """Test loading and saving models"""

        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'test-diagrams/simple-items.gaphor')

        with open(path, 'r') as ifile:
            storage.load(ifile, factory=self.element_factory)

        pf = PseudoFile()

        storage.save(XMLWriter(pf), factory=self.element_factory)

        with open(path, 'r') as ifile:
            orig = ifile.read()

        copy = pf.data

        with open('tmp.gaphor', 'w') as ofile:
            ofile.write(copy)

        expr = re.compile('gaphor-version="[^"]*"')
        orig = expr.sub('%VER%', orig)
        copy = expr.sub('%VER%', copy)

        self.assertEquals(copy, orig, 'Saved model does not match copy')


class FileUpgradeTestCase(TestCase):
    def test_association_upgrade(self):
        """Test association navigability upgrade in Gaphor 0.15.0
        """

        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'test-diagrams/associations-pre015.gaphor')

        with open(path) as ifile:
            storage.load(ifile, factory=self.element_factory)

        diagrams = list(self.kindof(uml2.Diagram))
        self.assertEquals(1, len(diagrams))
        diagram = diagrams[0]
        assocs = diagram.canvas.select(lambda e: isinstance(e, items.AssociationItem))
        assert len(assocs) == 8
        a1, a2 = [a for a in assocs if a.subject.name == 'nav']

        self.assertTrue(a1.head_end.subject.navigability)
        self.assertTrue(a1.tail_end.subject.navigability)
        self.assertTrue(a2.head_end.subject.navigability)
        self.assertTrue(a2.tail_end.subject.navigability)

        self.assertTrue(len(a1.head_end.subject.type.ownedAttribute) == 1)
        self.assertTrue(len(a1.tail_end.subject.type.ownedAttribute) == 2)  # association end and an attribute

        # use cases and actors - no owned attributes as navigability is realized
        # by association's navigable owned ends
        self.assertTrue(len(a2.head_end.subject.type.ownedAttribute) == 0)
        self.assertTrue(len(a2.tail_end.subject.type.ownedAttribute) == 0)

        a1, a2 = [a for a in assocs if a.subject.name == 'nonnav']
        self.assertTrue(a1.head_end.subject.navigability is False)
        self.assertTrue(a1.tail_end.subject.navigability is False)
        self.assertTrue(a2.head_end.subject.navigability is False)
        self.assertTrue(a2.tail_end.subject.navigability is False)

        a1, a2 = [a for a in assocs if a.subject.name == 'unk']
        self.assertTrue(a1.head_end.subject.navigability is None)
        self.assertTrue(a1.tail_end.subject.navigability is None)
        self.assertTrue(a2.head_end.subject.navigability is None)
        self.assertTrue(a2.tail_end.subject.navigability is None)

        a, = [a for a in assocs if a.subject.name == 'sided']
        assert a.head_end.subject.name == 'cs'
        assert a.tail_end.subject.name == 'int'
        self.assertTrue(a.head_end.subject.navigability is False)
        self.assertTrue(a.tail_end.subject.navigability is True)

        a, = [a for a in assocs if a.subject.name == 'sided2']
        assert a.head_end.subject.name == 'cs'
        assert a.tail_end.subject.name == 'int'
        self.assertTrue(a.head_end.subject.navigability is None)
        self.assertTrue(a.tail_end.subject.navigability is True)

    def test_tagged_values_upgrade(self):
        """Test tagged values upgrade in Gaphor 0.15.0
        """

        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'test-diagrams/taggedvalues-pre015.gaphor')

        with open(path) as ifile:
            storage.load(ifile, factory=self.element_factory)

        diagrams = list(self.kindof(uml2.Diagram))
        self.assertEquals(1, len(diagrams))
        diagram = diagrams[0]
        classes = diagram.canvas.select(lambda e: isinstance(e, items.ClassItem))
        profiles = self.element_factory.lselect(lambda e: isinstance(e, uml2.Profile))
        stereotypes = self.element_factory.lselect(lambda e: isinstance(e, uml2.Stereotype))

        self.assertEquals(2, len(classes))
        c1, c2 = classes

        self.assertEquals(1, len(profiles))
        profile = profiles[0]
        self.assertEquals('version 0.15 conversion', profile.name)

        self.assertEquals(1, len(stereotypes))
        stereotype = stereotypes[0]
        self.assertEquals('Tagged', stereotype.name)
        self.assertEquals(profile, stereotype.namespace)
        self.assertEquals('c1', c1.subject.name)
        self.assertEquals('c2', c2.subject.name)
        self.assertEquals(stereotype, c1.subject.appliedStereotype[0].classifier[0])
        self.assertEquals(stereotype, c2.subject.appliedStereotype[0].classifier[0])
        self.assertEquals('t1', c1.subject.appliedStereotype[0].slot[0].definingFeature.name)
        self.assertEquals('t2', c1.subject.appliedStereotype[0].slot[1].definingFeature.name)
        self.assertEquals('t5', c2.subject.appliedStereotype[0].slot[0].definingFeature.name)
        self.assertEquals('t6', c2.subject.appliedStereotype[0].slot[1].definingFeature.name)
        self.assertEquals('t7', c2.subject.appliedStereotype[0].slot[2].definingFeature.name)

    def test_lifeline_messages_upgrade(self):
        """Test message occurrence specification upgrade in Gaphor 0.15.0
        """

        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'test-diagrams/lifelines-pre015.gaphor')

        with open(path) as ifile:
            storage.load(ifile, factory=self.element_factory)

        diagrams = list(self.kindof(uml2.Diagram))
        self.assertEquals(1, len(diagrams))
        diagram = diagrams[0]

        lifelines = diagram.canvas.select(lambda e: isinstance(e, items.LifelineItem))
        occurrences = self.kindof(uml2.MessageOccurrenceSpecification)
        messages = self.kindof(uml2.Message)

        self.assertEquals(2, len(lifelines))
        self.assertEquals(12, len(messages))
        # 2 * 12 but there are 4 lost/found messages
        self.assertEquals(20, len(set(occurrences)))

        l1, l2 = lifelines
        if l1.subject.name == 'a2':
            l1, l2 = l2, l1

        def find(name):
            return next((m for m in messages if m.name == name))

        m1 = find('call()')
        m2 = find('callx()')
        m3 = find('cally()')
        # inverted messages
        m4 = find('calla()')
        m5 = find('callb()')

        self.assertTrue(m1.sendEvent.covered is l1.subject)
        self.assertTrue(m2.sendEvent.covered is l1.subject)
        self.assertTrue(m3.sendEvent.covered is l1.subject)

        self.assertTrue(m1.receiveEvent.covered is l2.subject)
        self.assertTrue(m2.receiveEvent.covered is l2.subject)
        self.assertTrue(m3.receiveEvent.covered is l2.subject)

        # test inverted messages
        self.assertTrue(m4.sendEvent.covered is l2.subject)
        self.assertTrue(m5.sendEvent.covered is l2.subject)

        self.assertTrue(m4.receiveEvent.covered is l1.subject)
        self.assertTrue(m5.receiveEvent.covered is l1.subject)

        m = find('simple()')
        self.assertTrue(m.sendEvent.covered is l1.subject)
        self.assertTrue(m.receiveEvent.covered is l2.subject)

        m = find('found1()')
        self.assertTrue(m.sendEvent is None)
        self.assertTrue(m.receiveEvent.covered is l1.subject)

        m = find('found2()')
        self.assertTrue(m.sendEvent is None)
        self.assertTrue(m.receiveEvent.covered is l1.subject)

        m = find('rfound1()')
        self.assertTrue(m.sendEvent.covered is l1.subject)
        self.assertTrue(m.receiveEvent is None)

        m = find('lost1()')
        self.assertTrue(m.sendEvent.covered is l1.subject)
        self.assertTrue(m.receiveEvent is None)

        m = find('lost2()')
        self.assertTrue(m.sendEvent.covered is l1.subject)
        self.assertTrue(m.receiveEvent is None)

        m = find('rlost1()')
        self.assertTrue(m.sendEvent is None)
        self.assertTrue(m.receiveEvent.covered is l1.subject)

# vim:sw=4:et:ai
