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

    def __init__(self, element, associaton):
        self.element = element
        self.property = associaton


class AssociationSetEvent(AssociationChangeEvent):

    def __init__(self, element, associaton, old_value, new_value):
        AssociationChangeEvent.__init__(self, element, associaton)
        self.old_value = old_value
        self.new_value = new_value


class AssociationAddEvent(AssociationChangeEvent):

    def __init__(self, element, associaton, new_value):
        AssociationChangeEvent.__init__(self, element, associaton)
        self.new_value = new_value


class AssociationDeleteEvent(AssociationChangeEvent):

    def __init__(self, element, associaton, old_value):
        AssociationChangeEvent.__init__(self, element, associaton)
        self.old_value = old_value


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

