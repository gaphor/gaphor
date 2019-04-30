"""
UML events emited on a change in the data model.
"""

from zope import interface
from gaphor.interfaces import IServiceEvent


class IElementEvent(interface.Interface):
    """Generic event fired when element state changes.
    """

    element = interface.Attribute("The changed element")


class IElementChangeEvent(IElementEvent):
    """
    Generic event fired when element state changes.
    """

    property = interface.Attribute("The property that changed")
    old_value = interface.Attribute("The property value before the change")
    new_value = interface.Attribute("The property value after the change")


class IAttributeChangeEvent(IElementChangeEvent):
    """
    An attribute has changed.
    """


class IAssociationChangeEvent(IElementChangeEvent):
    """
    An association hs changed.
    This event may be fired for both ends of the association.
    """


class IAssociationSetEvent(IAssociationChangeEvent):
    """
    An association with [0..1] multiplicity has been changed.
    """


class IAssociationAddEvent(IAssociationChangeEvent):
    """
    An association with [0..*] multiplicity has been changed: a new entry is
    added. ``new_value`` contains the property being added.
    """


class IAssociationDeleteEvent(IAssociationChangeEvent):
    """
    An association with [0..*] multiplicity has been changed: an entry has
    been removed. ``old_value`` contains the property that has been removed.
    """
