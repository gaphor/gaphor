from typing import Type

from gaphor.diagram.connectors import Connector, RelationshipConnect
from gaphor.diagram.presentation import Classified
from gaphor.SysML.requirements.relationships import (
    DeriveReqtItem,
    RefineItem,
    SatisfyItem,
    TraceItem,
    VerifyItem,
)
from gaphor.SysML.sysml import (
    Block,
    DeriveReqt,
    DirectedRelationshipPropertyPath,
    Refine,
    Satisfy,
    Trace,
    Verify,
)


class DirectedRelationshipPropertyPathConnect(RelationshipConnect):
    """Connect Classifiers with a DirectedRelationshipPropertyPath relationship."""

    relation_type: Type[DirectedRelationshipPropertyPath]

    def reconnect(self, handle, port):
        self.reconnect_relationship(
            handle, self.relation_type.sourceContext, self.relation_type.targetContext
        )

    def connect_subject(self, handle):
        print(f"connect {self.relation_type}")
        relation = self.relationship_or_new(
            self.relation_type,
            self.relation_type.sourceContext,
            self.relation_type.targetContext,
        )
        self.line.subject = relation


@Connector.register(Classified, DeriveReqtItem)
class DeriveReqtConnect(DirectedRelationshipPropertyPathConnect):

    relation_type = DeriveReqt


@Connector.register(Classified, RefineItem)
class RefinefyConnect(DirectedRelationshipPropertyPathConnect):

    relation_type = Refine


@Connector.register(Classified, SatisfyItem)
class SatisfyConnect(DirectedRelationshipPropertyPathConnect):

    relation_type = Satisfy


@Connector.register(Classified, TraceItem)
class TraceConnect(DirectedRelationshipPropertyPathConnect):

    relation_type = Trace


@Connector.register(Classified, VerifyItem)
class VerifyConnect(DirectedRelationshipPropertyPathConnect):

    relation_type = Verify
