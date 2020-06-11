"""
Test classifier stereotypes attributes using component items.
"""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.UML.components.component import ComponentItem


def compartments(item):
    return item.shape.children[1:]


class StereotypesAttributesTestCase(TestCase):
    def setUp(self):
        """
        Create two stereotypes and extend component UML metaclass using
        them.
        """
        super().setUp()
        factory = self.element_factory
        cls = factory.create(UML.Class)
        cls.name = "Component"
        st1 = self.st1 = factory.create(UML.Stereotype)
        st1.name = "st1"
        st2 = self.st2 = factory.create(UML.Stereotype)
        st2.name = "st2"

        attr = factory.create(UML.Property)
        attr.name = "st1_attr_1"
        st1.ownedAttribute = attr
        attr = factory.create(UML.Property)
        attr.name = "st1_attr_2"
        st1.ownedAttribute = attr

        attr = factory.create(UML.Property)
        attr.name = "st2_attr_1"
        st2.ownedAttribute = attr

        self.ext1 = UML.model.create_extension(cls, st1)
        self.ext2 = UML.model.create_extension(cls, st2)

    def tearDown(self):
        del self.st1
        del self.st2

    def test_adding_slot(self):
        """Test if stereotype attribute information is added when slot is added
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True
        instance_spec = UML.model.apply_stereotype(c.subject, self.st1)

        # test precondition
        assert not compartments(c)

        slot = UML.model.add_slot(instance_spec, self.st1.ownedAttribute[0])
        slot.value = "foo"

        assert len(compartments(c)) == 1

    def test_removing_last_slot(self):
        """Test removing last slot
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True
        instance_spec = UML.model.apply_stereotype(c.subject, self.st1)

        slot = UML.model.add_slot(instance_spec, self.st1.ownedAttribute[0])
        slot.value = "foo"

        # test precondition
        assert compartments(c)

        del instance_spec.slot[slot]
        assert not compartments(c)

    def test_deleting_extension(self):
        """Test if stereotype is removed when extension is deleteded
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        instance_spec = UML.model.apply_stereotype(c.subject, self.st1)
        slot = UML.model.add_slot(instance_spec, self.st1.ownedAttribute[0])
        slot.value = "foo"

        # test precondition
        assert len(compartments(c)) == 1
        assert len(c.subject.appliedStereotype) == 1

        self.ext1.unlink()
        assert len(c.subject.appliedStereotype) == 0
        assert len(compartments(c)) == 0

    def test_deleting_stereotype(self):
        """Test if stereotype is removed when stereotype is deleteded
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        st1 = self.st1
        instance_spec = UML.model.apply_stereotype(c.subject, st1)
        slot = UML.model.add_slot(instance_spec, self.st1.ownedAttribute[0])
        slot.value = "foo"

        # test precondition
        assert len(compartments(c)) == 1
        assert len(c.subject.appliedStereotype) == 1

        st1.unlink()
        assert len(c.subject.appliedStereotype) == 0
        assert len(compartments(c)) == 0

    def test_removing_stereotype_attribute(self):
        """Test if stereotype instance specification is destroyed when stereotype attribute is removed
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        # test precondition
        assert len(compartments(c)) == 0
        obj = UML.model.apply_stereotype(c.subject, self.st1)
        # test precondition
        assert len(compartments(c)) == 0

        assert len(self.kindof(UML.Slot)) == 0

        attr = self.st1.ownedAttribute[0]
        slot = UML.model.add_slot(obj, attr)
        slot.value = "foo"
        assert len(obj.slot) == 1
        assert len(self.kindof(UML.Slot)) == 1
        assert slot.definingFeature

        assert compartments(c)

        attr.unlink()
        assert len(obj.slot) == 0
        assert 0 == len(self.kindof(UML.Slot))
        assert not compartments(c)

    def test_stereotype_attributes_status_saving(self):
        """Test stereotype attributes status saving
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True
        UML.model.apply_stereotype(c.subject, self.st1)
        obj = UML.model.apply_stereotype(c.subject, self.st2)

        # change attribute of 2nd stereotype
        attr = self.st2.ownedAttribute[0]
        slot = UML.model.add_slot(obj, attr)
        slot.value = "st2 test21"

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(ComponentItem)[0]
        assert item.show_stereotypes
        assert len(compartments(c)) == 1

    def test_saving_stereotype_attributes(self):
        """Test stereotype attributes saving
        """
        c = self.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        UML.model.apply_stereotype(c.subject, self.st1)
        UML.model.apply_stereotype(c.subject, self.st2)

        assert len(self.st1.ownedAttribute) == 3
        attr1, attr2, attr3 = self.st1.ownedAttribute
        assert attr1.name == "st1_attr_1", attr1.name
        assert attr2.name == "st1_attr_2", attr2.name
        assert attr3.name == "baseClass", attr3.name

        obj = c.subject.appliedStereotype[0]
        slot = UML.model.add_slot(obj, attr1)
        slot.value = "st1 test1"
        slot = UML.model.add_slot(obj, attr2)
        slot.value = "st1 test2"

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(ComponentItem)[0]
        el = item.subject
        assert len(el.appliedStereotype) == 2

        # check if stereotypes are properly applied
        names = sorted(obj.classifier[0].name for obj in el.appliedStereotype)
        assert ["st1", "st2"] == names

        # two attributes were changed for stereotype st1, so 2 slots
        obj = el.appliedStereotype[0]
        assert len(obj.slot) == 2
        assert "st1_attr_1" == obj.slot[0].definingFeature.name
        assert "st1 test1" == obj.slot[0].value
        assert "st1_attr_2" == obj.slot[1].definingFeature.name
        assert "st1 test2" == obj.slot[1].value

        # no stereotype st2 attribute changes, no slots
        obj = el.appliedStereotype[1]
        assert len(obj.slot) == 0
