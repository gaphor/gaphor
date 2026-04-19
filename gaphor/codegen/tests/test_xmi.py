import pytest

from gaphor import UML
from gaphor.codegen.xmi import convert


@pytest.fixture(scope="module")
def kerml():
    return convert("models/KerML-25-04-04.xmi")


@pytest.fixture(scope="module")
def sysml():
    return convert("models/SysML2-25-02-15.xmi")


def test_kerml_xmi_conversion(kerml):
    assert not kerml.is_empty()
    assert kerml.lookup("KerML")


def test_sysml_xmi_conversion(sysml):
    assert not sysml.is_empty()
    assert sysml.lookup("SysML")


def test_generalization_conversion(kerml):
    behavior = next(
        kerml.select(lambda e: isinstance(e, UML.Class) and e.name == "Behavior")
    )

    assert behavior.general[0].name == "Class"


def test_enumeration_literal_conversion(kerml):
    enumeration = next(
        kerml.select(
            lambda e: (
                isinstance(e, UML.Enumeration) and e.name == "FeatureDirectionKind"
            )
        )
    )

    assert enumeration.ownedLiteral
    assert "inout" in [el.name for el in enumeration.ownedLiteral]


def test_owned_rule_specification_conversion(kerml):
    constraint = kerml.lookup("Kernel-Behaviors-Behavior-checkBehaviorSpecialization")

    assert isinstance(constraint, UML.Constraint)
    assert constraint.specification
    assert isinstance(constraint.specification, UML.OpaqueExpression)
    assert (
        constraint.specification.body
        == "specializesFromLibrary('Performances::Performance')"
    )
    assert constraint.specification.language == "English"


def test_body_condition_specification_conversion(kerml):
    operation = kerml.lookup("Kernel-Behaviors-ParameterMembership-parameterDirection_")

    assert isinstance(operation, UML.Operation)
    assert operation.bodyCondition
    assert operation.bodyCondition.id == (
        "Kernel-Behaviors-ParameterMembership-parameterDirection_-unnamed1"
    )
    assert operation.bodyCondition.specification
    assert isinstance(operation.bodyCondition.specification, UML.OpaqueExpression)
    assert operation.bodyCondition.specification.body == "FeatureDirectionKind::_'in'"
    assert operation.bodyCondition.specification.language == "OCL2.0"
