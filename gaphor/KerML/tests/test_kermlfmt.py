from gaphor.core.format import format
from gaphor.KerML import kerml
from gaphor.SysML2 import sysml2


def test_format_kerml_element_prefers_declared_name(element_factory):
    element = element_factory.create(kerml.Element)
    element.declaredName = "MyElement"

    assert format(element) == "MyElement"


def test_format_kerml_element_falls_back_to_element_id(element_factory):
    element = element_factory.create(kerml.Element)
    element.elementId = "E-1"

    assert format(element) == "E-1"


def test_format_sysml2_definition_uses_kerml_element_formatter(element_factory):
    definition = element_factory.create(sysml2.PartDefinition)
    definition.declaredName = "PartDef"

    assert format(definition) == "PartDef"


def test_format_sysml2_usage_uses_kerml_element_formatter(element_factory):
    usage = element_factory.create(sysml2.PartUsage)
    usage.declaredName = "PartUse"

    assert format(usage) == "PartUse"
