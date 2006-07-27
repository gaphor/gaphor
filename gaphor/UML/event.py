"""
Define events.
"""

from interfaces import *
from zope import interface

class AttributeChangedEvent(object):
    zope.implements(IAttributeChangedEvent)

    def __init__(self, element, attribute):
        self.element = element
        self.attribute = attribute


class AssociationChangedEvent(object):
    zope.implements(IAssociationChangedEvent)

    def __init__(self, element, associaton):
        self.element = element
        self.associaton = associaton


