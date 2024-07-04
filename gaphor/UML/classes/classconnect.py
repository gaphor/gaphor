"""Classes related (dependency, implementation) adapter connections."""

from __future__ import annotations

from gaphor import UML
from gaphor.core.modeling import Element, Presentation
from gaphor.diagram.connectors import (
    Connector,
    DirectionalRelationshipConnect,
    RelationshipConnect,
)
from gaphor.diagram.presentation import Classified, Named
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.recipes import owner_package


@Connector.register(Named, DependencyItem)
class DependencyConnect(DirectionalRelationshipConnect):
    """Connect two Named elements using a Dependency."""

    line: DependencyItem

    def connect_subject(self, handle):
        dependency_type = self.update_dependency_type(handle)

        relation = self.relationship_or_new(
            dependency_type,
            dependency_type.supplier,
            dependency_type.client,
        )
        self.line.subject = relation

    def update_dependency_type(self, handle):
        line = self.line

        if line.auto_dependency:
            opposite = line.opposite(handle)

            other = self.get_connected(opposite)
            assert other
            if handle is line.head:
                client = other.subject
                supplier = self.element.subject
            else:
                client = self.element.subject
                supplier = other.subject
            line.dependency_type = UML.recipes.dependency_type(client, supplier)
        return line.dependency_type


@Connector.register(Classified, AssociationItem)
class AssociationConnect(RelationshipConnect):
    """Connect association to classifier."""

    line: AssociationItem

    def __init__(self, element: Presentation[Element], line: AssociationItem) -> None:
        super().__init__(element, line)
        self._navigabilities = (
            list(line.subject.memberEnd[:].navigability) if line.subject else []
        )

    def allow(self, handle, port):
        # Element should be a Classifier
        return super().allow(handle, port) and isinstance(
            self.element.subject, UML.Classifier
        )

    def relationship(  # type:ignore[override]
        self, head_subject, tail_subject
    ) -> UML.Association | None:
        line = self.line
        subject = line.subject

        def member_ends_match(subject):
            return len(subject.memberEnd) >= 2 and (
                (
                    head_subject is subject.memberEnd[0].type
                    and tail_subject is subject.memberEnd[1].type
                )
                or (
                    head_subject is subject.memberEnd[1].type
                    and tail_subject is subject.memberEnd[0].type
                )
            )

        # First check if the right subject is already connected:
        if line.subject and member_ends_match(line.subject):
            return subject

        diagram = self.diagram

        return next(
            (
                a
                for a in line.model.select(UML.Association)
                if member_ends_match(a) and diagram not in a.presentation[:].diagram
            ),
            None,
        )

    def new_relation(self, head_subject, tail_subject) -> UML.Association:  # type: ignore[override]
        return UML.recipes.create_association(head_subject, tail_subject)  # type: ignore[no-any-return]

    def relationship_or_new(self, head_subject, tail_subject) -> UML.Association:  # type: ignore[override]
        line = self.line

        relation: UML.Association | None = self.relationship(head_subject, tail_subject)

        if relation:
            return relation

        relation = self.new_relation_from_copy(UML.Association)

        if relation:
            relation.memberEnd[0].type = head_subject
            relation.memberEnd[1].type = tail_subject
            for end, nav in zip(relation.memberEnd, self._navigabilities):
                UML.recipes.set_navigability(relation, end, nav)
        else:
            relation = self.new_relation(head_subject, tail_subject)
            tail_subject = relation.memberEnd[1]
            if (
                line.preferred_aggregation in ("shared", "composite")
                or line.preferred_tail_navigability == "navigable"
            ):
                UML.recipes.set_navigability(relation, tail_subject, True)
            tail_subject.aggregation = line.preferred_aggregation
            line.preferred_aggregation = "none"
            line.preferred_tail_navigability = "none"

        assert isinstance(relation, UML.Association)

        relation.package = owner_package(self.diagram.owner)

        return relation

    def connect_subject(self, handle):
        line = self.line
        head_end = self.get_connected(line.head)
        tail_end = self.get_connected(line.tail)
        assert head_end and tail_end
        relation = self.relationship_or_new(head_end.subject, tail_end.subject)

        if head_end.subject is relation.memberEnd[0].type:
            line.head_subject = relation.memberEnd[0]
            line.tail_subject = relation.memberEnd[1]
        else:
            line.head_subject = relation.memberEnd[1]
            line.tail_subject = relation.memberEnd[0]

        # Set subject last, to trigger updates on property editor, a.o.
        line.subject = relation

    def disconnect_subject(self, handle) -> None:
        del self.line.head_subject
        del self.line.tail_subject
        super().disconnect_subject(handle)
