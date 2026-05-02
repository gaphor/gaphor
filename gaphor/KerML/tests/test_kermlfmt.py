from gaphor.core.format import format
from gaphor.KerML import kerml


def test_format_kerml_element_prefers_declared_name(element_factory):
    element = element_factory.create(kerml.Element)
    element.declaredName = "MyElement"

    assert format(element) == "MyElement"


def test_format_kerml_element_falls_back_to_element_id(element_factory):
    element = element_factory.create(kerml.Element)
    element.elementId = "E-1"

    assert format(element) == "E-1"
