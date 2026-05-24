from pathlib import Path

import pytest

from gaphor import UML
from gaphor.codegen.coder import (
    associations,
    bases,
    class_declaration,
    is_in_profile,
    is_in_toplevel_package,
    is_simple_type,
    load_model,
    load_modeling_language,
    order_classes,
    resolve_attribute_type_values,
    subsets,
    superset_attribute,
    variables,
)
from gaphor.codegen.xmi import convert
from gaphor.core.format import parse
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.modelinglanguage import (
    CoreModelingLanguage,
    MockModelingLanguage,
)
from gaphor.diagram.general.modelinglanguage import GeneralModelingLanguage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture(scope="session")
def core_metamodel():
    return load_model(
        Path("models/Core.gaphor"),
        MockModelingLanguage(
            CoreModelingLanguage(), GeneralModelingLanguage(), UMLModelingLanguage()
        ),
    )


@pytest.fixture(scope="session")
def uml_metamodel():
    return load_model(
        Path("models/UML.gaphor"),
        MockModelingLanguage(
            CoreModelingLanguage(), GeneralModelingLanguage(), UMLModelingLanguage()
        ),
    )


@pytest.fixture(scope="session")
def kerml_xmi():
    return convert("models/KerML-25-04-04.xmi")


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


def create_literal(s: str, element_factory):
    literal = UML.EnumerationLiteral()
    parse(literal, s)
    return literal


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

    enum = element_factory.create(UML.Enumeration)
    enum.name = "EnumKind"
    enum.ownedLiteral = create_literal("in", element_factory)
    enum.ownedLiteral = create_literal("out", element_factory)

    resolve_attribute_type_values(element_factory)

    attr_def = list(variables(class_))

    assert attr_def == ['first = _enumeration("first", EnumKind, EnumKind.in_)']


def test_coder_write_class_with_enumeration_and_default_value(
    element_factory: ElementFactory,
):
    class_ = element_factory.create(UML.Class)
    class_.ownedAttribute = create_attribute("first: EnumKind = out", element_factory)

    enum = element_factory.create(UML.Enumeration)
    enum.name = "EnumKind"
    enum.ownedLiteral = create_literal("in", element_factory)
    enum.ownedLiteral = create_literal("out", element_factory)

    resolve_attribute_type_values(element_factory)

    attr_def = list(variables(class_))

    assert attr_def == ['first = _enumeration("first", EnumKind, EnumKind.out)']


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
    UML.recipes.set_multiplicity_upper_value(navigable_association.memberEnd[1], 1)
    class_a = navigable_association.memberEnd[0].type
    assert (
        UML.recipes.get_multiplicity_upper_value_as_string(
            navigable_association.memberEnd[1]
        )
        == "1"
    )

    attr_def = list(variables(class_a))

    assert class_a.name == "A"
    assert attr_def == ["b: relation_one[B]"]


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
    assert not is_simple_type(value_spec)
    assert not is_simple_type(literal_spec)


def test_order_classes(uml_metamodel):
    classes = list(order_classes(uml_metamodel.select(UML.Class)))

    assert classes[0].name == "Base"
    assert classes[1].name == "Element"
    assert classes[2].name == "NamedElement"


def test_coder_write_association(navigable_association: UML.Association):
    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B, opposite="a")']


def test_coder_write_association_lower_value(navigable_association: UML.Association):
    end = navigable_association.memberEnd[1]
    UML.recipes.set_multiplicity_lower_value(end, 1)

    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B, lower=1, opposite="a")']


def test_coder_write_association_upper_value(navigable_association: UML.Association):
    end = navigable_association.memberEnd[1]
    UML.recipes.set_multiplicity_upper_value(end, 1)

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


def test_coder_write_subset_for_derived_subsetted_property():
    class_type = UML.Class()
    class_type.name = "Type"
    class_step = UML.Class()
    class_step.name = "Step"
    class_behavior = UML.Class()
    class_behavior.name = "Behavior"

    feature = UML.Property()
    feature.name = "feature"
    feature.type = class_step
    class_type.ownedAttribute = feature

    step = UML.Property()
    step.name = "step"
    step.type = class_step
    step.isDerived = True
    step.subsettedProperty = feature
    class_behavior.ownedAttribute = step

    a = list(associations(class_behavior))

    assert a == ["Behavior.step = subset(\"step\", Step, 0, '*', None, Type.feature)"]


def test_coder_emits_subset_after_referenced_superset_in_same_class():
    class_element = UML.Class()
    class_element.name = "Element"
    class_relationship = UML.Class()
    class_relationship.name = "Relationship"
    class_owning_membership = UML.Class()
    class_owning_membership.name = "OwningMembership"

    owning_membership = UML.Property()
    owning_membership.name = "owningMembership"
    owning_membership.type = class_owning_membership
    owning_membership.isDerived = True

    owning_relationship = UML.Property()
    owning_relationship.name = "owningRelationship"
    owning_relationship.type = class_relationship

    owning_membership.subsettedProperty = owning_relationship
    class_element.ownedAttribute = owning_membership
    class_element.ownedAttribute = owning_relationship

    a = list(associations(class_element))

    assert a == [
        'Element.owningRelationship = association("owningRelationship", Relationship)',
        "Element.owningMembership = subset(\"owningMembership\", OwningMembership, 0, '*', None, Element.owningRelationship)",
    ]


def test_coder_write_derivedunion_for_non_subsetted_derived_property():
    class_step = UML.Class()
    class_step.name = "Step"
    class_behavior = UML.Class()
    class_behavior.name = "Behavior"

    step = UML.Property()
    step.name = "step"
    step.type = class_step
    step.isDerived = True
    class_behavior.ownedAttribute = step

    a = list(associations(class_behavior))

    assert a == ['Behavior.step = derivedunion("step", Step)']


def test_coder_does_not_emit_legacy_subset_wiring_for_derived_subset():
    class_type = UML.Class()
    class_type.name = "Type"
    class_step = UML.Class()
    class_step.name = "Step"
    class_behavior = UML.Class()
    class_behavior.name = "Behavior"

    feature = UML.Property()
    feature.name = "feature"
    feature.type = class_step
    class_type.ownedAttribute = feature

    step = UML.Property()
    step.name = "step"
    step.type = class_step
    step.isDerived = True
    step.subsettedProperty = feature
    class_behavior.ownedAttribute = step

    generated = list(subsets(class_behavior, {}))

    assert generated == []


def test_coder_writes_real_kerml_subset_without_legacy_wiring(kerml_xmi):
    behavior = next(
        kerml_xmi.select(lambda e: isinstance(e, UML.Class) and e.name == "Behavior")
    )

    association_lines = list(associations(behavior))
    subset_lines = [line for line in subsets(behavior, {}) if "Behavior.step" in line]

    assert (
        "Behavior.step = subset(\"step\", Step, 0, '*', None, Type.feature)"
        in association_lines
    )
    assert subset_lines == []


def test_coder_write_association_opposite_not_navigable(
    navigable_association: UML.Association,
):
    UML.recipes.set_navigability(
        navigable_association, navigable_association.memberEnd[0], None
    )

    a = list(associations(navigable_association.memberEnd[0].type))

    assert a == ['A.b = association("b", B)']


def test_attribute_from_super_model(
    uml_metamodel: ElementFactory, core_metamodel: ElementFactory
):
    package = UML.Package()
    package.name = "UML"
    class_ = UML.Class()
    class_.name = "Package"
    class_.owningPackage = package

    element_type, base = superset_attribute(
        class_,
        "member",
        {
            # Order matters! Base model first.
            "Core": (CoreModelingLanguage(), core_metamodel),
            "UML": (UMLModelingLanguage(), uml_metamodel),
        },
    )

    assert element_type is UML.Package
    assert base.owner.name == "Namespace"


def test_replace_simple_attribute(uml_metamodel: ElementFactory):
    klass = next(
        uml_metamodel.select(lambda e: isinstance(e, UML.Class) and e.name == "Class")
    )
    a = next(it for it in klass.ownedAttribute if it.name == "isActive")

    assert a.name == "isActive"
    assert a.typeValue == "bool"
    assert not a.type
