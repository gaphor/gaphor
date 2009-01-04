"""
Classes related (dependency, implementation) adapter connections.
"""

from gaphor.adapters.connectors import RelationshipConnect
from zope import interface, component
from gaphor import UML
from gaphor.diagram import items

class DependencyConnect(RelationshipConnect):
    """
    Connect two NamedItem elements using a Dependency
    """
    component.adapts(items.NamedItem, items.DependencyItem)

    def glue(self, handle, port):
        line = self.line
        element = self.element

        # Element should be a NamedElement
        if not element.subject or \
           not isinstance(element.subject, UML.NamedElement):
            return None

        return super(DependencyConnect, self).glue(handle, port)

    def connect_subject(self, handle):
        """
        TODO: cleck for existing relationships (use self.relation())
        """
        line = self.line
        if line.auto_dependency:
            line.set_dependency_type()
        if line.dependency_type is UML.Realization:
            relation = self.relationship_or_new(line.dependency_type,
                                head=('realizingClassifier', None),
                                tail=('abstraction', 'realization'))
        else:
            relation = self.relationship_or_new(line.dependency_type,
                                ('supplier', 'supplierDependency'),
                                ('client', 'clientDependency'))
        line.subject = relation

component.provideAdapter(DependencyConnect)


class GeneralizationConnect(RelationshipConnect):
    """
    Connect Classifiers with a Generalization relationship.
    """
    # FixMe: Both ends of the generalization should be of the same  type?
    component.adapts(items.ClassifierItem, items.GeneralizationItem)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Generalization,
                    ('general', None),
                    ('specific', 'generalization'))
        self.line.subject = relation

component.provideAdapter(GeneralizationConnect)



class AssociationConnect(RelationshipConnect):
    """
    Connect association to classifier.
    """
    component.adapts(items.ClassifierItem, items.AssociationItem)

    CAN_BE_UNARY = True    # allow one classifier to be connected by association

    def glue(self, handle, port):
        element = self.element

        # Element should be a Classifier
        if not isinstance(element.subject, UML.Classifier):
            return None

        return super(AssociationConnect, self).glue(handle, port)

    def connect_subject(self, handle):
        element = self.element
        line = self.line

        c1 = line.head.connected_to
        c2 = line.tail.connected_to
        if c1 and c2:
            head_type = c1.subject
            tail_type = c2.subject

            # First check if we do not already contain the right subject:
            if line.subject:
                end1 = line.subject.memberEnd[0]
                end2 = line.subject.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) \
                   or (end2.type is head_type and end1.type is tail_type):
                    return
                    
            # Find all associations and determine if the properties on
            # the association ends have a type that points to the class.
            for assoc in self.element_factory.select():
                if isinstance(assoc, UML.Association):
                    end1 = assoc.memberEnd[0]
                    end2 = assoc.memberEnd[1]
                    if (end1.type is head_type and end2.type is tail_type) \
                       or (end2.type is head_type and end1.type is tail_type):
                        # check if this entry is not yet in the diagram
                        # Return if the association is not (yet) on the canvas
                        for item in assoc.presentation:
                            if item.canvas is element.canvas:
                                break
                        else:
                            line.subject = assoc
                            if (end1.type is head_type and end2.type is tail_type):
                                line.head_end.subject = end1
                                line.tail_end.subject = end2
                            else:
                                line.head_end.subject = end2
                                line.tail_end.subject = end1
                            return
            else:
                # Create a new Extension relationship
                relation = self.element_factory.create(UML.Association)
                head_end = self.element_factory.create(UML.Property)
                head_end.lowerValue = self.element_factory.create(UML.LiteralSpecification)
                tail_end = self.element_factory.create(UML.Property)
                tail_end.lowerValue = self.element_factory.create(UML.LiteralSpecification)
                relation.package = element.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                head_end.type = head_type
                tail_end.type = tail_type
                head_type.ownedAttribute = tail_end
                tail_type.ownedAttribute = head_end

                line.head_end.subject = head_end
                line.tail_end.subject = tail_end
                # Do subject itself last, so event handlers can trigger
                line.subject = relation

    def disconnect_subject(self, handle):
        """
        Disconnect model element.
        Disconnect property (memberEnd) too, in case of end of life for
        Extension
        """
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            old = self.line.subject
            del self.line.subject
            del self.line.head_end.subject
            del self.line.tail_end.subject
            if old and len(old.presentation) == 0:
                for e in list(old.memberEnd):
                    e.unlink()
                old.unlink()


component.provideAdapter(AssociationConnect)



class ImplementationConnect(RelationshipConnect):
    """
    Connect Interface and a BehavioredClassifier using an Implementation.
    """
    component.adapts(items.NamedItem, items.ImplementationItem)

    def glue(self, handle, port):
        line = self.line
        element = self.element

        # Element at the head should be an Interface
        if handle is line.head and \
           not isinstance(element.subject, UML.Interface):
            return None

        # Element at the tail should be a BehavioredClassifier
        if handle is line.tail and \
           not isinstance(element.subject, UML.BehavioredClassifier):
            return None

        return super(ImplementationConnect, self).glue(handle, port)


    def connect_subject(self, handle):
        """
        Perform implementation relationship connection.
        """
        relation = self.relationship_or_new(UML.Implementation,
                    ('contract', None),
                    ('implementatingClassifier', 'implementation'))
        self.line.subject = relation


component.provideAdapter(ImplementationConnect)

# vim:sw=4:et:ai
