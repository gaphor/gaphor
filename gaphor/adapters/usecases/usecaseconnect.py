"""
Use cases related connection adapters.
"""

from __future__ import absolute_import
from zope import component
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.adapters.connectors import RelationshipConnect


class IncludeConnect(RelationshipConnect):
    """
    Connect use cases with an include item relationship.
    """
    component.adapts(items.UseCaseItem, items.IncludeItem)

    def allow(self, handle, port):
        line = self.line
        element = self.element

        if not (element.subject and isinstance(element.subject, uml2.UseCase)):
            return None

        return super(IncludeConnect, self).allow(handle, port)


    def reconnect(self, handle, port):
        self.reconnect_relationship(handle, uml2.Include.addition, uml2.Include.includingCase)


    def connect_subject(self, handle):
        relation = self.relationship_or_new(uml2.Include,
                    uml2.Include.addition,
                    uml2.Include.includingCase)
        self.line.subject = relation

component.provideAdapter(IncludeConnect)


class ExtendConnect(RelationshipConnect):
    """
    Connect use cases with an extend item relationship.
    """
    component.adapts(items.UseCaseItem, items.ExtendItem)

    def allow(self, handle, port):
        line = self.line
        element = self.element
        
        if not (element.subject and isinstance(element.subject, uml2.UseCase)):
            return None

        return super(ExtendConnect, self).allow(handle, port)

    def reconnect(self, handle, port):
        self.reconnect_relationship(handle, uml2.Extend.extendedCase, uml2.Extend.extension)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(uml2.Extend,
                    uml2.Extend.extendedCase,
                    uml2.Extend.extension)
        self.line.subject = relation

component.provideAdapter(ExtendConnect)

# vim:sw=4:et:ai

