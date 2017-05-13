#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test classifier stereotypes attributes using component items.
"""

from __future__ import absolute_import

from gaphor.UML import uml2, modelfactory
from gaphor.diagram.component import ComponentItem
from gaphor.tests import TestCase


class StereotypesAttributesTestCase(TestCase):
    def setUp(self):
        """
        Create two stereotypes and extend component UML metaclass using
        them.
        """
        super(StereotypesAttributesTestCase, self).setUp()
        factory = self.element_factory
        cls = factory.create(uml2.Class)
        cls.name = 'Component'
        st1 = self.st1 = factory.create(uml2.Stereotype)
        st1.name = 'st1'
        st2 = self.st2 = factory.create(uml2.Stereotype)
        st2.name = 'st2'

        attr = factory.create(uml2.Property)
        attr.name = 'st1_attr_1'
        st1.ownedAttribute = attr
        attr = factory.create(uml2.Property)
        attr.name = 'st1_attr_2'
        st1.ownedAttribute = attr

        attr = factory.create(uml2.Property)
        attr.name = 'st2_attr_1'
        st2.ownedAttribute = attr

        self.ext1 = modelfactory.extend_with_stereotype(factory, cls, st1)
        self.ext2 = modelfactory.extend_with_stereotype(factory, cls, st2)

    def tearDown(self):
        del self.st1
        del self.st2

    def test_applying_stereotype(self):
        """Test if stereotype compartment is created when stereotype is applied
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        # test precondition
        self.assertEqual(0, len(c._compartments))

        c.show_stereotypes_attrs = True

        modelfactory.apply_stereotype(factory, c.subject, self.st1)
        self.assertEqual(1, len(c._compartments))
        self.assertFalse(c._compartments[0].visible)

    def test_adding_slot(self):
        """Test if stereotype attribute information is added when slot is added
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True
        obj = modelfactory.apply_stereotype(factory, c.subject, self.st1)

        # test precondition
        self.assertFalse(c._compartments[0].visible)

        slot = modelfactory.add_slot(factory, obj, self.st1.ownedAttribute[0])

        compartment = c._compartments[0]
        self.assertTrue(compartment.visible)
        self.assertEqual(1, len(compartment), slot)

    def test_removing_last_slot(self):
        """Test removing last slot
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True
        obj = modelfactory.apply_stereotype(factory, c.subject, self.st1)

        slot = modelfactory.add_slot(factory, obj, self.st1.ownedAttribute[0])

        compartment = c._compartments[0]
        # test precondition
        self.assertTrue(compartment.visible)

        del obj.slot[slot]
        self.assertFalse(compartment.visible)

    def test_removing_stereotype(self):
        """Test if stereotype compartment is destroyed when stereotype is removed
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True

        modelfactory.apply_stereotype(factory, c.subject, self.st1)

        # test precondition
        self.assertEqual(1, len(c._compartments))

        modelfactory.remove_stereotype(c.subject, self.st1)
        self.assertEqual(0, len(c._compartments))

    def test_deleting_extension(self):
        """Test if stereotype is removed when extension is deleted
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True

        st1 = self.st1
        ext1 = self.ext1
        modelfactory.apply_stereotype(factory, c.subject, st1)

        # test precondition
        self.assertEqual(1, len(c._compartments))
        self.assertEqual(1, len(c.subject.appliedStereotype))

        ext1.unlink()
        self.assertEqual(0, len(c.subject.appliedStereotype))
        self.assertEqual(0, len(c._compartments))

    def test_deleting_stereotype(self):
        """Test if stereotype is removed when stereotype is deleted
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True

        st1 = self.st1
        modelfactory.apply_stereotype(factory, c.subject, st1)

        # test precondition
        self.assertEqual(1, len(c._compartments))
        self.assertEqual(1, len(c.subject.appliedStereotype))

        st1.unlink()
        self.assertEqual(0, len(c.subject.appliedStereotype))
        self.assertEqual(0, len(c._compartments))

    def test_removing_stereotype_attribute(self):
        """Test if stereotype instance specification is destroyed when stereotype attribute is removed
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True

        # test precondition
        self.assertEqual(0, len(c._compartments))
        obj = modelfactory.apply_stereotype(factory, c.subject, self.st1)
        # test precondition
        self.assertEqual(1, len(c._compartments))

        self.assertEqual(0, len(self.kindof(uml2.Slot)))

        attr = self.st1.ownedAttribute[0]
        slot = modelfactory.add_slot(factory, obj, attr)
        self.assertEqual(1, len(obj.slot))
        self.assertEqual(1, len(self.kindof(uml2.Slot)))
        self.assertTrue(slot.definingFeature)

        compartment = c._compartments[0]
        self.assertTrue(compartment.visible)

        attr.unlink()
        self.assertEqual(0, len(obj.slot))
        self.assertEqual(0, len(self.kindof(uml2.Slot)))
        self.assertFalse(compartment.visible)

    def test_stereotype_attributes_status_saving(self):
        """Test stereotype attributes status saving
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True
        modelfactory.apply_stereotype(factory, c.subject, self.st1)
        obj = modelfactory.apply_stereotype(factory, c.subject, self.st2)

        # change attribute of 2nd stereotype
        attr = self.st2.ownedAttribute[0]
        slot = modelfactory.add_slot(self.element_factory, obj, attr)
        slot.value = 'st2 test21'

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, ComponentItem))[0]
        self.assertTrue(item.show_stereotypes_attrs)
        self.assertEqual(2, len(item._compartments))
        # first stereotype has no attributes changed, so compartment
        # invisible
        self.assertFalse(item._compartments[0].visible)
        self.assertTrue(item._compartments[1].visible)

    def test_saving_stereotype_attributes(self):
        """Test stereotype attributes saving
        """
        factory = self.element_factory
        c = self.create(ComponentItem, uml2.Component)

        c.show_stereotypes_attrs = True

        modelfactory.apply_stereotype(factory, c.subject, self.st1)
        modelfactory.apply_stereotype(factory, c.subject, self.st2)

        self.assertEqual(3, len(self.st1.ownedAttribute))
        attr1, attr2, attr3 = self.st1.ownedAttribute
        self.assertEqual(attr1.name, 'st1_attr_1', attr1.name)
        self.assertEqual(attr2.name, 'st1_attr_2', attr2.name)
        self.assertEqual(attr3.name, 'baseClass', attr3.name)

        obj = c.subject.appliedStereotype[0]
        slot = modelfactory.add_slot(self.element_factory, obj, attr1)
        slot.value = 'st1 test1'
        slot = modelfactory.add_slot(self.element_factory, obj, attr2)
        slot.value = 'st1 test2'

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, ComponentItem))[0]
        el = item.subject
        self.assertEqual(2, len(el.appliedStereotype))

        # check if stereotypes are properly applied
        names = sorted(obj.classifier[0].name for obj in el.appliedStereotype)
        self.assertEqual(['st1', 'st2'], names)

        # two attributes were changed for stereotype st1, so 2 slots
        obj = el.appliedStereotype[0]
        self.assertEqual(2, len(obj.slot))
        self.assertEqual('st1_attr_1', obj.slot[0].definingFeature.name)
        self.assertEqual('st1 test1', obj.slot[0].value)
        self.assertEqual('st1_attr_2', obj.slot[1].definingFeature.name)
        self.assertEqual('st1 test2', obj.slot[1].value)

        # no stereotype st2 attribute changes, no slots
        obj = el.appliedStereotype[1]
        self.assertEqual(0, len(obj.slot))

# vim:sw=4:et
