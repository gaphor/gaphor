"""Classes related (dependency, implementation) adapter connections."""

from gaphas import Handle

from gaphor import UML
from gaphor.diagram.connectors import (
    Connector,
    RelationshipConnect,
    UnaryRelationshipConnect,
)
from gaphor.diagram.presentation import Classified, Named
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.recipes import owner_package


@Connector.register(Named, DependencyItem)
class DependencyConnect(RelationshipConnect):
    """Connect two Named elements using a Dependency."""

    line: DependencyItem

    def allow(self, handle, port):
        element = self.element

        # Element should be a NamedElement
        if not (element.subject and isinstance(element.subject, UML.NamedElement)):
            return False

        return super().allow(handle, port)

    def connect_subject(self, handle):
        """
        TODO: check for existing relationships (use self.relation())
        """

        line = self.line

        self.update_dependency_type(handle)

        relation = self.relationship_or_new(
            line.dependency_type,
            line.dependency_type.supplier,
            line.dependency_type.client,
        )
        line.subject = relation

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


@Connector.register(Classified, GeneralizationItem)
class GeneralizationConnect(RelationshipConnect):
    """Connect Classifiers with a Generalization relationship."""

    def connect_subject(self, handle):
        self.line.subject = self.relationship_or_new(
            UML.Generalization, UML.Generalization.specific, UML.Generalization.general
        )


@Connector.register(Classified, AssociationItem)
class AssociationConnect(UnaryRelationshipConnect):
    """Connect association to classifier."""

    line: AssociationItem

    def allow(self, handle, port):
        element = self.element

        # Element should be a Classifier
        if not isinstance(element.subject, UML.Classifier):
            return None

        if not self.line.subject:
            return True

        line = self.line
        subject = line.subject
        is_head = handle is line.head

        def is_connection_allowed(p):
            end = p.head_end if is_head else p.tail_end
            h = end.owner_handle
            if h is handle:
                return True
            connected = self.get_connected(h)
            return (not connected) or connected.subject is element.subject

        return all(is_connection_allowed(p) for p in subject.presentation)

    def connect_subject(self, handle):
        element = self.element
        line = self.line

        assert element.diagram

        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if c1 and c2:

            if not line.subject:
                relation = UML.recipes.create_association(c1.subject, c2.subject)
                relation.package = owner_package(element.diagram.owner)
                line.head_subject = relation.memberEnd[0]
                line.tail_subject = relation.memberEnd[1]

                # Set subject last so that event handlers can trigger
                line.subject = relation

            line.head_subject.type = c1.subject
            line.tail_subject.type = c2.subject

    def disconnect_subject(self, handle: Handle) -> None:
        """Disconnect the type of each member end.

        On connect, we pair association member ends with the element
        they connect to. On disconnect, we remove this relation.
        """
        association = self.line.subject
        if association and len(association.presentation) <= 1:
            for e in list(association.memberEnd):
                UML.recipes.set_navigability(association, e, None)
            for e in list(association.memberEnd):
                e.type = None


@Connector.register(Named, InterfaceRealizationItem)
class InterfaceRealizationConnect(RelationshipConnect):
    """Connect Interface and a BehavioredClassifier using an
    InterfaceRealization."""

    def allow(self, handle, port):
        line = self.line
        element = self.element

        # Element at the head should be an Interface
        if handle is line.head and not isinstance(element.subject, UML.Interface):
            return None

        # Element at the tail should be a BehavioredClassifier
        if handle is line.tail and not isinstance(
            element.subject, UML.BehavioredClassifier
        ):
            return None

        return super().allow(handle, port)

    def connect_subject(self, handle):
        """Perform implementation relationship connection."""
        relation = self.relationship_or_new(
            UML.InterfaceRealization,
            UML.InterfaceRealization.contract,
            UML.InterfaceRealization.implementatingClassifier,
        )
        self.line.subject = relation
