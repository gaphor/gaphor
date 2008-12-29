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



# vim:sw=4:et:ai
