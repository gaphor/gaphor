"""
Use cases related connection adapters.
"""

from gaphor import UML
from gaphor.diagram.usecases.usecase import UseCaseItem
from gaphor.diagram.usecases.extend import ExtendItem
from gaphor.diagram.usecases.include import IncludeItem
from gaphor.diagram.connectors import IConnect, RelationshipConnect


@IConnect.register(UseCaseItem, IncludeItem)
class IncludeConnect(RelationshipConnect):
    """Connect use cases with an include item relationship."""

    def allow(self, handle, port):
        line = self.line
        element = self.element

        if not (element.subject and isinstance(element.subject, UML.UseCase)):
            return None

        return super().allow(handle, port)

    def reconnect(self, handle, port):
        self.reconnect_relationship(
            handle, UML.Include.addition, UML.Include.includingCase
        )

    def connect_subject(self, handle):
        relation = self.relationship_or_new(
            UML.Include, UML.Include.addition, UML.Include.includingCase
        )
        self.line.subject = relation


@IConnect.register(UseCaseItem, ExtendItem)
class ExtendConnect(RelationshipConnect):
    """Connect use cases with an extend item relationship."""

    def allow(self, handle, port):
        line = self.line
        element = self.element

        if not (element.subject and isinstance(element.subject, UML.UseCase)):
            return None

        return super().allow(handle, port)

    def reconnect(self, handle, port):
        self.reconnect_relationship(
            handle, UML.Extend.extendedCase, UML.Extend.extension
        )

    def connect_subject(self, handle):
        relation = self.relationship_or_new(
            UML.Extend, UML.Extend.extendedCase, UML.Extend.extension
        )
        self.line.subject = relation
