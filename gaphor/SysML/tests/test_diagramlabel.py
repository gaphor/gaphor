import pytest

from gaphor.SysML.painter import SysMLDiagramTypePainter
from gaphor.SysML.sysml import Block, ConstraintBlock, Requirement, SysMLDiagram
from gaphor.UML.uml import Activity, Interaction, Package, Profile, StateMachine


@pytest.mark.parametrize(
    "type,label",
    [
        [Activity, "[activity] ElemName [DiagName]"],
        [Block, "[block] ElemName [DiagName]"],
        [ConstraintBlock, "[constraint block] ElemName [DiagName]"],
        [Interaction, "[interaction] ElemName [DiagName]"],
        [Package, "[package] ElemName [DiagName]"],
        [Profile, "[profile] ElemName [DiagName]"],
        [Requirement, "[requirement] ElemName [DiagName]"],
        [StateMachine, "[state machine] ElemName [DiagName]"],
    ],
)
def test_diagram_label(type, label):
    def _diagram(elementType):
        element = elementType()
        element.name = "ElemName"

        diagram = SysMLDiagram()
        diagram.name = "DiagName"
        diagram.element = element

        return diagram

    assert SysMLDiagramTypePainter(_diagram(type)).label() == label


def test_uncontained_diagram_label():
    diagram = SysMLDiagram()
    diagram.name = "DiagName"

    assert SysMLDiagramTypePainter(diagram).label() == "DiagName"
