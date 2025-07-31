from gaphor import UML
from gaphor.diagram.deletable import deletable
from gaphor.SysML.diagramframe import DiagramFrameItem
from gaphor.SysML.sysml import Constraint


@deletable.register
def deletable_diagram_frame_item(item: DiagramFrameItem):
    return False


@deletable.register(UML.Property)
def deletable_constraint_parameter(element: UML.Property):
    """
    Prevent constraint parameters from being deleted automatically by the sanitizer.
    Deletion from the model browser is handled as a special case.
    """
    if isinstance(element.owner, Constraint):
        return False
    return True
