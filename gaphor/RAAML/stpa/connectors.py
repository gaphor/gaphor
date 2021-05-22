from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import Classified
from gaphor.RAAML.raaml import RelevantTo
from gaphor.RAAML.stpa import RelevantToItem
from gaphor.SysML.requirements.connectors import DirectedRelationshipPropertyPathConnect


@Connector.register(Classified, RelevantToItem)
class RelevantToConnect(DirectedRelationshipPropertyPathConnect):

    relation_type = RelevantTo
