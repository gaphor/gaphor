from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import Text, draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.UML.modelfactory import stereotypes_str


class DirectedRelationshipPropertyPathItem(LinePresentation):

    relation_type = ""

    def __init__(self, id=None, model=None):
        super().__init__(id, model, style={"dash-style": (7.0, 5.0)})

        self.shape_middle = Text(
            text=lambda: stereotypes_str(self.subject, (self.relation_type,)),
            style={"min-width": 0, "min-height": 0},
        )
        self.draw_head = draw_arrow_head
        self.watch("subject.appliedStereotype.classifier.name")


@represents(sysml.Satisfy)
class SatisfyItem(DirectedRelationshipPropertyPathItem):

    relation_type = "satisfy"


@represents(sysml.DeriveReqt)
class DeriveReqtItem(DirectedRelationshipPropertyPathItem):

    relation_type = "deriveReqt"


@represents(sysml.Trace)
class TraceItem(DirectedRelationshipPropertyPathItem):

    relation_type = "trace"


@represents(sysml.Verify)
class VerifyItem(DirectedRelationshipPropertyPathItem):

    relation_type = "verify"


@represents(sysml.Refine)
class RefineItem(DirectedRelationshipPropertyPathItem):

    relation_type = "refine"
