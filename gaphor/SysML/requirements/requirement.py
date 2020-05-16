from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Requirement
from gaphor.UML.classes import ClassItem


@represents(Requirement)
class RequirementItem(ClassItem):
    def additional_stereotypes(self):
        return ["requirement"]
