"""Test classifier stereotypes attributes using component items."""

import pytest

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.sanitizerservice import SanitizerService


def compartments(item):
    return item.shape.children[1:]


@pytest.fixture(autouse=True)
def sanitizer(event_manager):
    SanitizerService(event_manager)


@pytest.fixture
def case(element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "Component"
    st1_ = element_factory.create(UML.Stereotype)
    st1_.name = "st1"
    st2_ = element_factory.create(UML.Stereotype)
    st2_.name = "st2"

    attr = element_factory.create(UML.Property)
    attr.name = "st1_attr_1"
    st1_.ownedAttribute = attr
    attr = element_factory.create(UML.Property)
    attr.name = "st1_attr_2"
    st1_.ownedAttribute = attr

    attr = element_factory.create(UML.Property)
    attr.name = "st2_attr_1"
    st2_.ownedAttribute = attr

    class Case:
        st1 = st1_
        st2 = st2_
        ext1 = UML.recipes.create_extension(cls, st1_)
        ext2 = UML.recipes.create_extension(cls, st2_)

    return Case


def test_adding_slot(case, create):
    """Test if stereotype attribute information is added when slot is added."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True
    instance_spec = UML.recipes.apply_stereotype(c.subject, case.st1)

    # test precondition
    assert not compartments(c)

    slot = UML.recipes.add_slot(instance_spec, case.st1.ownedAttribute[0])
    slot.value = "foo"

    assert len(compartments(c)) == 1


def test_removing_last_slot(case, create):
    """Test removing last slot."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True
    instance_spec = UML.recipes.apply_stereotype(c.subject, case.st1)

    slot = UML.recipes.add_slot(instance_spec, case.st1.ownedAttribute[0])
    slot.value = "foo"

    # test precondition
    assert compartments(c)

    del instance_spec.slot[slot]
    assert not compartments(c)


def test_deleting_extension(case, create):
    """Test if stereotype is removed when extension is deleted."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True

    instance_spec = UML.recipes.apply_stereotype(c.subject, case.st1)
    slot = UML.recipes.add_slot(instance_spec, case.st1.ownedAttribute[0])
    slot.value = "foo"

    # test precondition
    assert len(compartments(c)) == 1
    assert len(c.subject.appliedStereotype) == 1

    case.ext1.unlink()
    assert len(c.subject.appliedStereotype) == 0
    assert len(compartments(c)) == 0


def test_deleting_stereotype(case, create):
    """Test if stereotype is removed when stereotype is deleted."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True

    st1 = case.st1
    instance_spec = UML.recipes.apply_stereotype(c.subject, st1)
    slot = UML.recipes.add_slot(instance_spec, case.st1.ownedAttribute[0])
    slot.value = "foo"

    # test precondition
    assert len(compartments(c)) == 1
    assert len(c.subject.appliedStereotype) == 1

    st1.unlink()
    assert len(c.subject.appliedStereotype) == 0
    assert len(compartments(c)) == 0


def test_removing_stereotype_attribute(case, element_factory, create):
    """Test if stereotype instance specification is destroyed when stereotype
    attribute is removed."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True

    # test precondition
    assert len(compartments(c)) == 0
    obj = UML.recipes.apply_stereotype(c.subject, case.st1)
    # test precondition
    assert len(compartments(c)) == 0

    assert len(element_factory.lselect(UML.Slot)) == 0

    attr = case.st1.ownedAttribute[0]
    slot = UML.recipes.add_slot(obj, attr)
    slot.value = "foo"
    assert len(obj.slot) == 1
    assert len(element_factory.lselect(UML.Slot)) == 1
    assert slot.definingFeature

    assert compartments(c)

    attr.unlink()
    assert len(obj.slot) == 0
    assert 0 == len(element_factory.lselect(UML.Slot))
    assert not compartments(c)


def test_stereotype_attributes_status_saving(
    case, element_factory, create, saver, loader
):
    """Test stereotype attributes status saving."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True
    UML.recipes.apply_stereotype(c.subject, case.st1)
    obj = UML.recipes.apply_stereotype(c.subject, case.st2)

    # change attribute of 2nd stereotype
    attr = case.st2.ownedAttribute[0]
    slot = UML.recipes.add_slot(obj, attr)
    slot.value = "st2 test21"

    data = saver()
    loader(data)
    diagram = next(element_factory.select(Diagram))

    item = next(diagram.select(ComponentItem))
    assert item.show_stereotypes
    assert len(compartments(c)) == 1


def test_saving_stereotype_attributes(case, element_factory, create, saver, loader):
    """Test stereotype attributes saving."""
    c = create(ComponentItem, UML.Component)

    c.show_stereotypes = True

    UML.recipes.apply_stereotype(c.subject, case.st1)
    UML.recipes.apply_stereotype(c.subject, case.st2)

    assert len(case.st1.ownedAttribute) == 3
    attr1, attr2, attr3 = case.st1.ownedAttribute
    assert attr1.name == "st1_attr_1", attr1.name
    assert attr2.name == "st1_attr_2", attr2.name
    assert attr3.name == "baseClass", attr3.name

    obj = c.subject.appliedStereotype[0]
    slot = UML.recipes.add_slot(obj, attr1)
    slot.value = "st1 test1"
    slot = UML.recipes.add_slot(obj, attr2)
    slot.value = "st1 test2"

    data = saver()
    loader(data)
    diagram = next(element_factory.select(Diagram))

    item = next(diagram.select(ComponentItem))
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
