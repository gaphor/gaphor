"""
Zope events.
"""

from zope import interface

class IElementChangedEvent(interface.Interface):
    """Generic event fired when element state changes
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

