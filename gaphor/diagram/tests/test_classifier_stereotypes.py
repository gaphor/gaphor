"""
Test classifier stereotypes attributes using component items.
"""

from gaphor import UML
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
        cls = factory.create(UML.Class)
        cls.name = 'Component'
        st1 = self.st1 = factory.create(UML.Stereotype)
        st1.name = 'st1'
        st2 = self.st2 = factory.create(UML.Stereotype)
        st2.name = 'st2'

        attr = factory.create(UML.Property)
        attr.name = 'st1_attr_1'
        st1.ownedAttribute = attr

        UML.model.extend_with_stereotype(factory, cls, st1)
        UML.model.extend_with_stereotype(factory, cls, st2)


    def test_applying_stereotype(self):
        """Test if stereotype compartment is created when stereotype is applied
        """
        factory = self.element_factory
        c = self.create(ComponentItem, UML.Component)

        # test precondition
        assert len(c._compartments) == 0

        c.show_stereotypes_attrs = True

        UML.model.apply_stereotype(factory, c.subject, self.st1)
        self.assertEquals(1, len(c._compartments))
        self.assertFalse(c._compartments[0].visible)


    def test_adding_slot(self):
        """Test if stereotype attribute information is added when slot is added
        """
        factory = self.element_factory
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes_attrs = True
        obj = UML.model.apply_stereotype(factory, c.subject, self.st1)

        # test precondition
        assert not c._compartments[0].visible

        UML.model.add_slot(factory, obj, self.st1.ownedAttribute[0])

        compartment = c._compartments[0]
        self.assertTrue(compartment.visible)
        self.assertEquals(2, len(compartment))


    def test_removing_last_slot(self):
        """Test removing last slot
        """
        factory = self.element_factory
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes_attrs = True
        obj = UML.model.apply_stereotype(factory, c.subject, self.st1)

        slot = UML.model.add_slot(factory, obj, self.st1.ownedAttribute[0])

        compartment = c._compartments[0]
        # test precondition
        assert compartment.visible

        del obj.slot[slot]
        self.assertFalse(compartment.visible)


# vim:sw=4:et
