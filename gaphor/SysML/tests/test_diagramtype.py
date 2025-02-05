import pytest

from gaphor.core.modeling.properties import attribute
from gaphor.SysML.diagramtype import DiagramDefault, SysMLDiagramType
from gaphor.SysML.sysml import SysMLDiagram
from gaphor.UML import NamedElement


class MockElementA(NamedElement):
    pass


class MockElementB(NamedElement):
    pass


class AbcSysMLDiagram(SysMLDiagram):
    diagramType: attribute[str] = attribute("diagramType", str, default="abc")


@pytest.fixture
def diagram_type():
    return SysMLDiagramType(
        AbcSysMLDiagram,
        "Defghi",
        (),
        (MockElementA,),
        (DiagramDefault(type(None), MockElementA, "New mock element A"),),
    )


def test_sysml_diagram_type_allowed(diagram_type):
    assert diagram_type.allowed(MockElementA())
    assert diagram_type.allowed(None)
    assert not diagram_type.allowed(MockElementB())


def test_sysml_diagram_type_with_parent(element_factory, diagram_type):
    mock_a = element_factory.create(MockElementA)
    mock_a.name = "Mock A"

    diagram = diagram_type.create(element_factory, mock_a)
    assert diagram.diagramType == "abc"
    assert diagram.name == "Defghi"
    assert isinstance(diagram.element, MockElementA)
    assert diagram.element.name == "Mock A"


def test_sysml_diagram_type_without_parent(element_factory, diagram_type):
    diagram = diagram_type.create(element_factory, None)
    assert diagram.diagramType == "abc"
    assert diagram.name == "Defghi"
    assert isinstance(diagram.element, MockElementA)
    assert diagram.element.name == "New mock element A"


def test_sysml_diagram_type_wrong_parent(element_factory, diagram_type):
    mock_b = element_factory.create(MockElementB)
    mock_b.name = "Mock B"

    with pytest.raises(TypeError) as e:
        diagram_type.create(element_factory, mock_b)
    assert str(e.value) == "Can’t create “Defghi” nested under a “Mock B”"
