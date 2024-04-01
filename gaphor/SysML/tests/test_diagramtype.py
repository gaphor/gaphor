import pytest

from gaphor.SysML.diagramtype import DiagramDefault, SysMLDiagramType
from gaphor.UML.uml import NamedElement


class MockElementA(NamedElement):
    pass


class MockElementB(NamedElement):
    pass


def test_sysml_diagram_type(element_factory):
    diagram_type = SysMLDiagramType(
        "abc",
        "Defghi",
        (),
        (MockElementA,),
        (DiagramDefault(type(None), MockElementA, "New mock element A"),),
    )

    assert diagram_type.allowed(MockElementA())
    assert diagram_type.allowed(None)
    assert not diagram_type.allowed(MockElementB())

    mock_a = element_factory.create(MockElementA)
    mock_a.name = "Mock A"

    diagram = diagram_type.create(element_factory, mock_a)
    assert diagram.diagramType == "abc"
    assert diagram.name == "Defghi"
    assert isinstance(diagram.element, MockElementA)
    assert diagram.element.name == "Mock A"

    diagram = diagram_type.create(element_factory, None)
    assert diagram.diagramType == "abc"
    assert diagram.name == "Defghi"
    assert isinstance(diagram.element, MockElementA)
    assert diagram.element.name == "New mock element A"

    mock_b = element_factory.create(MockElementB)
    mock_b.name = "Mock B"

    with pytest.raises(TypeError) as e:
        diagram = diagram_type.create(element_factory, mock_b)
    assert str(e.value) == "Can’t create “Defghi” nested under a “Mock B”"
