"""
Define events.
"""

from interfaces import *
from zope import interface


class AttributeChangeEvent(object):
    interface.implements(IAttributeChangeEvent)

    def __init__(self, element, attribute, old_value, new_value):
        self.element = element
        self.property = attribute
        self.old_value = old_value
        self.new_value = new_value


class AssociationChangeEvent(object):
    interface.implements(IAssociationChangeEvent)

    def __init__(self, element, association):
        self.element = element
        self.property = association


class AssociationSetEvent(AssociationChangeEvent):

    interface.implements(IAssociationSetEvent)

    def __init__(self, element, association, old_value, new_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


class AssociationAddEvent(AssociationChangeEvent):

    interface.implements(IAssociationAddEvent)

    def __init__(self, element, association, new_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.new_value = new_value


class AssociationDeleteEvent(AssociationChangeEvent):

    interface.implements(IAssociationDeleteEvent)

    def __init__(self, element, association, old_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value


class DerivedChangeEvent(AssociationChangeEvent):
    pass


class DerivedSetEvent(DerivedChangeEvent):

    interface.implements(IAssociationSetEvent)

    def __init__(self, element, association, old_value, new_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


class DerivedAddEvent(DerivedChangeEvent):

    interface.implements(IAssociationAddEvent)

    def __init__(self, element, association, new_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.new_value = new_value


class DerivedDeleteEvent(DerivedChangeEvent):

    interface.implements(IAssociationDeleteEvent)

    def __init__(self, element, association, old_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value


class RedefineSetEvent(AssociationChangeEvent):

    interface.implements(IAssociationSetEvent)

    def __init__(self, element, association, old_value, new_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


class RedefineAddEvent(AssociationChangeEvent):

    interface.implements(IAssociationAddEvent)

    def __init__(self, element, association, new_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.new_value = new_value


class RedefineDeleteEvent(AssociationChangeEvent):

    interface.implements(IAssociationDeleteEvent)

    def __init__(self, element, association, old_value):
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value


class DiagramItemCreateEvent(object):
    interface.implements(IElementCreateEvent)

    def __init__(self, element):
        self.element = element


class ElementCreateEvent(object):
    interface.implements(IElementCreateEvent, IElementFactoryEvent)

    def __init__(self, service, element):
        self.service = service
        self.element = element


class ElementDeleteEvent(object):
    interface.implements(IElementDeleteEvent, IElementFactoryEvent)

    def __init__(self, service, element):
        self.service = service
        self.element = element


class ModelFactoryEvent(object):
    interface.implements(IModelFactoryEvent)

    def __init__(self, service):
        self.service = service


class FlushFactoryEvent(object):
    interface.implements(IFlushFactoryEvent)

    def __init__(self, service):
        self.service = service

