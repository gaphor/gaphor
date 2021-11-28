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


def test_coder_write_class_with_attributes(element_factory):
    class_: UML.Class = UML.Class()
    class_.ownedAttribute = create_attribute("first: str")
    class_.ownedAttribute = create_attribute("second: int")
    coder = Coder(class_)

    attr_def = list(coder)

    assert attr_def == ["first: attribute[str]", "second: attribute[int]"]


# Ideas:
# Primitive types?
# Overrides
# Class ordering
# Metaclass: class is owned by a Profile
