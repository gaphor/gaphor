from gaphor.diagram.painter import DiagramTypePainter
from gaphor.SysML.sysml import Block, ConstraintBlock, Requirement, SysMLDiagram
from gaphor.UML.painter import UMLDiagramTypePainter
from gaphor.UML.uml import (
    Activity,
    Interaction,
    NamedElement,
    Package,
    Profile,
    StateMachine,
)


@DiagramTypePainter.register(SysMLDiagram)  # type: ignore[attr-defined]
class SysMLDiagramTypePainter(UMLDiagramTypePainter):
    def label(self):
        if (el := self.diagram.element) and isinstance(el, NamedElement):
            return f"[{_element_type(el)}] {el.name} [{self.diagram.name}]"

        # TODO: SysML specification does not allow parentless elements,
        #       but since it is not constrained (yet), it may happen.
        return super().label()


def _element_type(el) -> str:
    if isinstance(el, Activity):
        return "activity"
    if isinstance(el, ConstraintBlock):
        return "constraint block"
    if isinstance(el, Block):
        return "block"
    if isinstance(el, Interaction):
        return "interaction"
    if isinstance(el, Profile):
        return "profile"
    if isinstance(el, Package):
        return "package"
    if isinstance(el, Requirement):
        return "requirement"
    return "state machine" if isinstance(el, StateMachine) else ""
