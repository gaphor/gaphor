from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.SysML.requirements.relationships import DirectedRelationshipPropertyPathItem


@represents(
    raaml.RelevantTo,
    head=raaml.RelevantTo.sourceContext,
    tail=raaml.RelevantTo.targetContext,
)
class RelevantToItem(DirectedRelationshipPropertyPathItem):
    relation_type = "relevantTo"
