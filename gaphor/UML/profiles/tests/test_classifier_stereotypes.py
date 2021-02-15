"""Test classifier stereotypes attributes using component items."""

import pytest

from gaphor import UML
from gaphor.conftest import Case
from gaphor.UML.components.component import ComponentItem


def compartments(item):
    return item.shape.children[1:]


class StereotypesAttributesCase(Case):
    def __init__(self):
        super().__init__()
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

    def shutdown(self):
        super().shutdown()
        del self.st1
        del self.st2


class TestStereotypesAttributes:
    @pytest.fixture
    def case(self):
        case = StereotypesAttributesCase()
        yield case
        case.shutdown()

    def test_adding_slot(self, case):
        """Test if stereotype attribute information is added when slot is
        added."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True
        instance_spec = UML.model.apply_stereotype(c.subject, case.st1)

        # test precondition
        assert not compartments(c)

        slot = UML.model.add_slot(instance_spec, case.st1.ownedAttribute[0])
        slot.value = "foo"

        assert len(compartments(c)) == 1

    def test_removing_last_slot(self, case):
        """Test removing last slot."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True
        instance_spec = UML.model.apply_stereotype(c.subject, case.st1)

        slot = UML.model.add_slot(instance_spec, case.st1.ownedAttribute[0])
        slot.value = "foo"

        # test precondition
        assert compartments(c)

        del instance_spec.slot[slot]
        assert not compartments(c)

    def test_deleting_extension(self, case):
        """Test if stereotype is removed when extension is deleted."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        instance_spec = UML.model.apply_stereotype(c.subject, case.st1)
        slot = UML.model.add_slot(instance_spec, case.st1.ownedAttribute[0])
        slot.value = "foo"

        # test precondition
        assert len(compartments(c)) == 1
        assert len(c.subject.appliedStereotype) == 1

        case.ext1.unlink()
        assert len(c.subject.appliedStereotype) == 0
        assert len(compartments(c)) == 0

    def test_deleting_stereotype(self, case):
        """Test if stereotype is removed when stereotype is deleted."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        st1 = case.st1
        instance_spec = UML.model.apply_stereotype(c.subject, st1)
        slot = UML.model.add_slot(instance_spec, case.st1.ownedAttribute[0])
        slot.value = "foo"

        # test precondition
        assert len(compartments(c)) == 1
        assert len(c.subject.appliedStereotype) == 1

        st1.unlink()
        assert len(c.subject.appliedStereotype) == 0
        assert len(compartments(c)) == 0

    def test_removing_stereotype_attribute(self, case):
        """Test if stereotype instance specification is destroyed when
        stereotype attribute is removed."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        # test precondition
        assert len(compartments(c)) == 0
        obj = UML.model.apply_stereotype(c.subject, case.st1)
        # test precondition
        assert len(compartments(c)) == 0

        assert len(case.kindof(UML.Slot)) == 0

        attr = case.st1.ownedAttribute[0]
        slot = UML.model.add_slot(obj, attr)
        slot.value = "foo"
        assert len(obj.slot) == 1
        assert len(case.kindof(UML.Slot)) == 1
        assert slot.definingFeature

        assert compartments(c)

        attr.unlink()
        assert len(obj.slot) == 0
        assert 0 == len(case.kindof(UML.Slot))
        assert not compartments(c)

    def test_stereotype_attributes_status_saving(self, case):
        """Test stereotype attributes status saving."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True
        UML.model.apply_stereotype(c.subject, case.st1)
        obj = UML.model.apply_stereotype(c.subject, case.st2)

        # change attribute of 2nd stereotype
        attr = case.st2.ownedAttribute[0]
        slot = UML.model.add_slot(obj, attr)
        slot.value = "st2 test21"

        data = case.save()
        case.load(data)

        item = next(case.diagram.select(ComponentItem))
        assert item.show_stereotypes
        assert len(compartments(c)) == 1

    def test_saving_stereotype_attributes(self, case):
        """Test stereotype attributes saving."""
        c = case.create(ComponentItem, UML.Component)

        c.show_stereotypes = True

        UML.model.apply_stereotype(c.subject, case.st1)
        UML.model.apply_stereotype(c.subject, case.st2)

        assert len(case.st1.ownedAttribute) == 3
        attr1, attr2, attr3 = case.st1.ownedAttribute
        assert attr1.name == "st1_attr_1", attr1.name
        assert attr2.name == "st1_attr_2", attr2.name
        assert attr3.name == "baseClass", attr3.name

        obj = c.subject.appliedStereotype[0]
        slot = UML.model.add_slot(obj, attr1)
        slot.value = "st1 test1"
        slot = UML.model.add_slot(obj, attr2)
        slot.value = "st1 test2"

        data = case.save()
        case.load(data)

        item = next(case.diagram.select(ComponentItem))
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
