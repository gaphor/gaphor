"""
UML events emited on a change in the data model.
"""

from zope import interface
from gaphor.interfaces import IService, IServiceEvent

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
    """Generic event fired when element state changes.
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
    """


# vim: sw=4:et
