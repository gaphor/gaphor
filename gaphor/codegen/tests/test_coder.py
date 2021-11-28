import pytest

from gaphor import UML
from gaphor.codegen.coder import Coder
from gaphor.core.format import parse


def test_coder_write_class():
    class_ = UML.Class()
    class_.name = "TestClass"

    coder = Coder(class_)

    class_def = str(coder)

    assert class_def == "class TestClass:"


def test_coder_write_class_no_attributes():
    class_ = UML.Class()
    coder = Coder(class_)

    attr_def = list(coder)

    assert attr_def == ["pass"]


def create_attribute(s: str):
    attr = UML.Property()
    parse(attr, s)
    return attr


def test_coder_write_class_with_attributes():
    class_ = UML.Class()
    class_.ownedAttribute = create_attribute("first: str")
    class_.ownedAttribute = create_attribute("second: int")
    coder = Coder(class_)

    attr_def = list(coder)

    assert attr_def == ["first: attribute[str]", "second: attribute[int]"]


@pytest.fixture
def navigable_association(element_factory):
    class_a = element_factory.create(UML.Class)
    class_a.name = "A"
    class_b = element_factory.create(UML.Class)
    class_b.name = "B"
    association = UML.model.create_association(class_a, class_b)
    UML.model.set_navigability(association, association.memberEnd[0], True)
    UML.model.set_navigability(association, association.memberEnd[1], True)
    association.memberEnd[0].name = "a"
    association.memberEnd[1].name = "b"
    return association


def test_coder_write_class_with_n_m_association(navigable_association):
    class_a = navigable_association.memberEnd[0].type
    coder = Coder(class_a)

    attr_def = list(coder)

    assert class_a.name == "A"
    assert attr_def == ["b: relation_many[B]"]


def test_coder_write_class_with_1_n_association(navigable_association):
    class_a = navigable_association.memberEnd[0].type
    navigable_association.memberEnd[1].upper = "1"
    coder = Coder(class_a)

    attr_def = list(coder)

    assert class_a.name == "A"
    assert attr_def == ["b: relation_one[B]"]


# Ideas:
# Primitive types?
# Overrides
# Class ordering
# Metaclass: class is owned by a Profile
