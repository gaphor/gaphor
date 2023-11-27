from gaphor.diagram.support import represents
from gaphor.SysML.relationships import DirectedRelationshipPropertyPathItem
from gaphor.SysML.sysml import Allocate


@represents(Allocate, head=Allocate.sourceContext, tail=Allocate.targetContext)
class AllocateItem(DirectedRelationshipPropertyPathItem):
    @property
    def relation_type(self):
        return self.diagram.gettext("allocate")
