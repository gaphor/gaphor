from gaphor.codegen.xmi import convert


def test_kerml_xmi_conversion():
    element_factory = convert("models/KerML-25-04-04.xmi")

    assert not element_factory.is_empty()
    assert element_factory.lookup("KerML")


def test_generalization_conversion(kerml):
    behavior = next(
        kerml.select(lambda e: isinstance(e, UML.Class) and e.name == "Behavior")
    )

    assert behavior.general[0].name == "Class"


def test_enumeration_literal_conversion(kerml):
    enumeration = next(
        kerml.select(
            lambda e: isinstance(e, UML.Enumeration)
            and e.name == "FeatureDirectionKind"
        )
    )

    assert enumeration.ownedLiteral
    assert "inout" in [el.name for el in enumeration.ownedLiteral]
