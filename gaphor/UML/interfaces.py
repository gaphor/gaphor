"""
UML events emited on a change in the data model.
"""

from zope import interface
from gaphor.interfaces import IService, IServiceEvent

class IElementChangedEvent(interface.Interface):
    """Generic event fired when element state changes.
    """
    element = interface.Attribute("The changed element")


class IAttributeChangedEvent(IElementChangedEvent):
    """An attribute has changed.
    """
    attribute = interface.Attribute("The attribute")


class IAssociationChangedEvent(IElementChangedEvent):
    """An association hs changed.
    This event may be fired for both ends of the association.
    """
    association = interface.Attribute("The association")


class IModelFactoryEvent(IServiceEvent):
    """A new model is loaded into the ElementFactory.
    """


class IFlushFactoryEvent(IServiceEvent):
    """All elements are removed from the ElementFactory.
    """


class IFactoryElementEvent(IServiceEvent):
    """Events related to individual model elements.
    """
    element = interface.Attribute("The element")


class ICreateElementEvent(IFactoryElementEvent):
    """A new element has been created.
    """


class IRemoveElementEvent(IFactoryElementEvent):
    """An element is deleted from the model.
    """


# vim: sw=4:et
