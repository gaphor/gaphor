"""
UML events emited on a change in the data model.
"""

from __future__ import absolute_import

from zope import interface

from gaphor.interfaces import IServiceEvent


class IElementEvent(interface.Interface):
    """Generic event fired when element state changes.
    """
    element = interface.Attribute("The changed element")


class IElementCreateEvent(IElementEvent):
    """A new element has been created.
    """


class IElementDeleteEvent(IElementEvent):
    """An element is deleted from the model.
    """


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


class IElementFactoryEvent(IServiceEvent):
    """
    Events related to individual model elements.
    """


class IModelFactoryEvent(IElementFactoryEvent):
    """
    A new model is loaded into the ElementFactory.
    """


class IFlushFactoryEvent(IElementFactoryEvent):
    """
    All elements are removed from the ElementFactory.
    This event is emitted before the factory is emptied.
    """

# vim: sw=4:et
