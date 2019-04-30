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
