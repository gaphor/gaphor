import pytest

from gaphor import UML
from gaphor.codegen.coder import (
    Coder,
    bases,
    is_enumeration,
    is_in_profile,
    is_in_toplevel_package,
    is_simple_attribute,
    last_minute_updates,
    order_classes,
)
from gaphor.core.format import parse
from gaphor.core.modeling import ElementFactory
from gaphor.storage import storage


def test_coder_write_class():
    class_ = UML.Class()
    class_.name = "TestClass"

    coder = Coder(class_)

    class_def = str(coder)

    assert class_def == "class TestClass():"


def test_coder_write_class_no_attributes():
    class_ = UML.Class()
    coder = Coder(class_)

    attr_def = list(coder)

    assert attr_def == []


def create_attribute(s: str, element_factory=None):
    if element_factory:
        attr = element_factory.create(UML.Property)
    else:
        attr = UML.Property()
    parse(attr, s)
    return attr


def test_coder_write_class_with_attributes():
    class_ = UML.Class()
    class_.ownedAttribute = create_attribute("first: str")
    class_.ownedAttribute = create_attribute("second: int")
    coder = Coder(class_)

    attr_def = list(coder)

    assert attr_def == [
        'first: attribute[str] = attribute("first", str)',
        'second: attribute[int] = attribute("second", int)',
    ]


def test_coder_write_class_with_enumeration(element_factory: ElementFactory):
    class_ = element_factory.create(UML.Class)
    class_.ownedAttribute = create_attribute("first: EnumKind", element_factory)

    enum = element_factory.create(UML.Class)
    enum.name = "EnumKind"
    enum.ownedAttribute = create_attribute("in", element_factory)
    enum.ownedAttribute = create_attribute("out", element_factory)

    last_minute_updates(element_factory)

    coder = Coder(class_)

    attr_def = list(coder)

    assert attr_def == [
        'first: enumeration = enumeration("first", ("in", "out"), "in")'
    ]


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


def class_with_name(name):
    c = UML.Class()
    c.name = name
    return c


def test_enumeration():
    assert not is_enumeration(class_with_name("A"))
    assert is_enumeration(class_with_name("AKind"))


def test_in_profile():
    class_ = UML.Class()
    profile = UML.Profile()
    profile.ownedType = class_

    assert is_in_profile(class_)


def test_not_in_profile():
    class_ = UML.Class()
    package = UML.Package()
    package.ownedType = class_

    assert not is_in_profile(class_)


def test_in_toplevel_package():
    class_ = UML.Class()
    package = UML.Package()
    nested = UML.Package()
    package.name = "Foo"
    package.nestedPackage = nested
    nested.ownedType = class_

    assert is_in_toplevel_package(class_, "Foo")
    assert not is_in_toplevel_package(class_, "Bar")


@pytest.fixture(scope="session")
def uml_metamodel(modeling_language):
    element_factory = ElementFactory()
    storage.load("models/UML.gaphor", element_factory, modeling_language)
    yield element_factory
    element_factory.shutdown()


def with_name(name):
    return lambda e: isinstance(e, UML.Class) and e.name == name


def test_bases(uml_metamodel: ElementFactory):
    package = next(uml_metamodel.select(with_name("Package")))

    names = list(s.name for s in bases(package))

    assert "Namespace" in names
    assert "PackageableElement" in names


def test_simple_attribute(uml_metamodel: ElementFactory):
    package = next(uml_metamodel.select(with_name("Package")))
    value_spec = next(uml_metamodel.select(with_name("ValueSpecification")))
    literal_spec = next(uml_metamodel.select(with_name("LiteralSpecification")))

    assert not is_simple_attribute(package)
    assert is_simple_attribute(value_spec)
    assert is_simple_attribute(literal_spec)


def test_order_classes(uml_metamodel):
    classes = list(order_classes(uml_metamodel.select(UML.Class)))

    assert classes[0].name == "Element"
    assert classes[1].name == "NamedElement"


# Ideas:
# Primitive types?
# Overrides
# Metaclass: class is owned by a Profile
