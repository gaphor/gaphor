from gaphor.diagram.diagramlabel import diagram_label
from gaphor.SysML.sysml import Block, ConstraintBlock, Requirement, SysMLDiagram
from gaphor.UML.uml import Activity, Interaction, Package, Profile, StateMachine


def test_diagram_label():
    def _diagram(elementType):
        element = elementType()
        element.name = "Efghi"

        diagram = SysMLDiagram()
        diagram.name = "Abcd"
        diagram.element = element

        return diagram

    assert diagram_label(_diagram(Activity)) == "[activity] Efghi [Abcd]"
    assert diagram_label(_diagram(Block)) == "[block] Efghi [Abcd]"
    assert diagram_label(_diagram(ConstraintBlock)) == "[constraint block] Efghi [Abcd]"
    assert diagram_label(_diagram(Interaction)) == "[interaction] Efghi [Abcd]"
    assert diagram_label(_diagram(Package)) == "[package] Efghi [Abcd]"
    assert diagram_label(_diagram(Profile)) == "[profile] Efghi [Abcd]"
    assert diagram_label(_diagram(Requirement)) == "[requirement] Efghi [Abcd]"
    assert diagram_label(_diagram(StateMachine)) == "[state machine] Efghi [Abcd]"


def test_uncontained_diagram_label():
    diagram = SysMLDiagram()
    diagram.name = "Abcd"

    assert diagram_label(diagram) == "Abcd"
