from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.SysML.requirements.relationships import DirectedRelationshipPropertyPathItem


@represents(raaml.RelevantTo)
class RelevantToItem(DirectedRelationshipPropertyPathItem):

    relation_type = "relevantTo"
