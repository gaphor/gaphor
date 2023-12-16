from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.SysML.relationships import DirectedRelationshipPropertyPathItem


@represents(
    sysml.Satisfy, head=sysml.Satisfy.sourceContext, tail=sysml.Satisfy.targetContext
)
class SatisfyItem(DirectedRelationshipPropertyPathItem):
    @property
    def relation_type(self):
        return self.diagram.gettext("satisfy")


@represents(
    sysml.DeriveReqt,
    head=sysml.DeriveReqt.sourceContext,
    tail=sysml.DeriveReqt.targetContext,
)
class DeriveReqtItem(DirectedRelationshipPropertyPathItem):
    @property
    def relation_type(self):
        return self.diagram.gettext("deriveReqt")


@represents(sysml.Trace, head=sysml.Trace.sourceContext, tail=sysml.Trace.targetContext)
class TraceItem(DirectedRelationshipPropertyPathItem):
    @property
    def relation_type(self):
        return self.diagram.gettext("trace")


@represents(
    sysml.Verify, head=sysml.Verify.sourceContext, tail=sysml.Verify.targetContext
)
class VerifyItem(DirectedRelationshipPropertyPathItem):
    @property
    def relation_type(self):
        return self.diagram.gettext("verify")


@represents(
    sysml.Refine, head=sysml.Refine.sourceContext, tail=sysml.Refine.targetContext
)
class RefineItem(DirectedRelationshipPropertyPathItem):
    @property
    def relation_type(self):
        return self.diagram.gettext("refine")
