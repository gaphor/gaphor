import pytest

from gaphor import UML
from gaphor.codegen.coder import (
    associations,
    attribute,
    bases,
    class_declaration,
    is_enumeration,
    is_in_profile,
    is_in_toplevel_package,
    is_simple_type,
    load_model,
    load_modeling_language,
    order_classes,
    resolve_attribute_type_values,
    variables,
)
from gaphor.core.format import parse
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.modelinglanguage import (
    CoreModelingLanguage,
    MockModelingLanguage,
)
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture(scope="session")
def uml_metamodel():
    return load_model(
        "models/UML.gaphor",
        MockModelingLanguage(CoreModelingLanguage(), UMLModelingLanguage()),
    )


def test_load_modeling_language():
    ml = load_modeling_language("Core")

    assert ml.__class__.__name__ == "CoreModelingLanguage"


def test_coder_write_class():
    class_ = UML.Class()
    class_.name = "TestClass"

    class_def = class_declaration(class_)

    assert class_def == "class TestClass():"


def test_coder_write_class_no_attributes():
    class_ = UML.Class()

    attr_def = list(variables(class_))

    assert not attr_def


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

    attr_def = list(variables(class_))

    assert attr_def == [
        'first: _attribute[str] = _attribute("first", str)',
        'second: _attribute[int] = _attribute("second", int)',
    ]


def test_coder_write_class_with_enumeration(element_factory: ElementFactory):
    class_ = element_factory.create(UML.Class)
    class_.ownedAttribute = create_attribute("first: EnumKind", element_factory)

    enum = element_factory.create(UML.Class)
    enum.name = "EnumKind"
    enum.ownedAttribute = create_attribute("in", element_factory)
    enum.ownedAttribute = create_attribute("out", element_factory)

    resolve_attribute_type_values(element_factory)

    attr_def = list(variables(class_))

    assert attr_def == ['first = _enumeration("first", ("in", "out"), "in")']


@pytest.fixture
def navigable_association(element_factory):
    class_a = element_factory.create(UML.Class)
    class_a.name = "A"
    class_b = element_factory.create(UML.Class)
    class_b.name = "B"
    association = UML.recipes.create_association(class_a, class_b)
    UML.recipes.set_navigability(association, association.memberEnd[0], True)
    UML.recipes.set_navigability(association, association.memberEnd[1], True)
    association.memberEnd[0].name = "a"
    association.memberEnd[1].name = "b"
    return association


def test_coder_write_class_with_n_m_association(navigable_association):
    class_a = navigable_association.memberEnd[0].type

    attr_def = list(variables(class_a))

    assert class_a.name == "A"
    assert attr_def == ["b: relation_many[B]"]


def test_coder_write_class_with_1_n_association(navigable_association):
    class_a = navigable_association.memberEnd[0].type
    navigable_association.memberEnd[1].upper = "1"

    attr_def = list(variables(class_a))

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


def by_name(name):
    return lambda e: isinstance(e, UML.Class) and e.name == name


def test_bases(uml_metamodel: ElementFactory):
    package = next(uml_metamodel.select(by_name("Package")))

    names = [s.name for s in bases(package)]

    assert "Namespace" in names
    assert "PackageableElement" in names


def test_extension_bases(element_factory: ElementFactory):
    metaclass = element_factory.create(UML.Class)
    stereotype = element_factory.create(UML.Stereotype)
    UML.recipes.create_extension(metaclass, stereotype)

    supers = list(bases(stereotype))

    assert supers == [metaclass]


def test_simple_attribute(uml_metamodel: ElementFactory):
    package = next(uml_metamodel.select(by_name("Package")))
    value_spec = next(uml_metamodel.select(by_name("ValueSpecification")))
    literal_spec = next(uml_metamodel.select(by_name("LiteralSpecification")))

    assert not is_simple_type(package)
    assert is_simple_type(value_spec)
    assert is_simple_type(literal_spec)


def test_order_classes(uml_metamodel):
    classes = list(order_classes(uml_metamodel.select(UML.Class)))

    assert classes[0].name == "Element"
    assert classes[1].name == "NamedElement"


def test_coder_write_association(navigable_association: UML.Association):
    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B, opposite="a")']


def test_coder_write_association_lower_value(navigable_association: UML.Association):
    end = navigable_association.memberEnd[1]
    end.lowerValue = "1"

    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B, lower=1, opposite="a")']


def test_coder_write_association_upper_value(navigable_association: UML.Association):
    end = navigable_association.memberEnd[1]
    end.upperValue = "1"

    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B, upper=1, opposite="a")']


def test_coder_write_association_composite(navigable_association: UML.Association):
    end = navigable_association.memberEnd[1]
    end.aggregation = "composite"

    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B, composite=True, opposite="a")']


def test_coder_write_association_not_navigable(navigable_association: UML.Association):
    UML.recipes.set_navigability(
        navigable_association, navigable_association.memberEnd[1], None
    )

    a = list(associations(navigable_association.memberEnd[0].type))

    assert not a


def test_coder_write_association_opposite_not_navigable(
    navigable_association: UML.Association,
):
    UML.recipes.set_navigability(
        navigable_association, navigable_association.memberEnd[0], None
    )

    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B)']


def test_attribute_from_super_model(uml_metamodel: ElementFactory):
    class_ = UML.Class()
    class_.name = "Package"

    element_type, base = attribute(
        class_, "relationship", [(UMLModelingLanguage(), uml_metamodel)]
    )

    assert element_type is UML.Package
    assert base.owner.name == "Element"


def test_replace_simple_attribute(uml_metamodel: ElementFactory):
    instancespec = next(
        uml_metamodel.select(
            lambda e: isinstance(e, UML.Class) and e.name == "InstanceSpecification"
        )
    )
    a = next(it for it in instancespec.ownedAttribute if it.name == "specification")

    assert a.name == "specification"
    assert a.typeValue == "str"
    assert not a.type
