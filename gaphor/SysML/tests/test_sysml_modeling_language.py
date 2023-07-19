from gaphor.SysML.modelinglanguage import SysMLModelingLanguage
from gaphor.core.modeling.diagram import Diagram
from gaphor.SysML.sysml import Block, ConstraintBlock, Requirement
from gaphor.UML.uml import Activity, Interaction, Package, Profile, StateMachine


def test_format_diagram_label(modeling_language):
    def _diagram(elementType):
        element = elementType()
        element.name = "Efghi"

        diagram = Diagram()
        diagram.name = "Abcd"
        diagram.element = element

        return diagram

    modeling_language = SysMLModelingLanguage()

    assert (
        modeling_language.format_diagram_label(_diagram(Activity))
        == "[activity] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(Block))
        == "[block] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(ConstraintBlock))
        == "[constraint block] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(Interaction))
        == "[interaction] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(Package))
        == "[package] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(Profile))
        == "[profile] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(Requirement))
        == "[requirement] Efghi [Abcd]"
    )
    assert (
        modeling_language.format_diagram_label(_diagram(StateMachine))
        == "[state machine] Efghi [Abcd]"
    )
