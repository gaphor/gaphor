"""
Define events.
"""

from interfaces import *
from zope import interface


class AttributeChangedEvent(object):
    interface.implements(IAttributeChangedEvent)

    def __init__(self, element, attribute):
        self.element = element
        self.attribute = attribute


class AssociationChangedEvent(object):
    interface.implements(IAssociationChangedEvent)

    def __init__(self, element, associaton):
        self.element = element
        self.associaton = associaton


class CreateElementEvent(object):
    interface.implements(ICreateElementEvent)

    def __init__(self, factory, element):
        self.factory = factory
        self.element = element


class RemoveElementEvent(object):
    interface.implements(IRemoveElementEvent)

    def __init__(self, factory, element):
        self.factory = factory
        self.element = element


class ModelFactoryEvent(object):
    interface.implements(IModelFactoryEvent)

    def __init__(self, factory):
        self.factory = factory


class FlushFactoryEvent(object):
    interface.implements(IFlushFactoryEvent)

    def __init__(self, factory):
        self.factory = factory

