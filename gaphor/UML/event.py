"""The core UML metamodel events."""

from zope.interface import implementer

from gaphor.event import ServiceEvent
from gaphor.UML.interfaces import IAssociationAddEvent, IAssociationDeleteEvent
from gaphor.UML.interfaces import (
    IAttributeChangeEvent,
    IAssociationChangeEvent,
    IAssociationSetEvent,
)


class ElementEvent(object):
    """Generic event fired when element state changes.
    """

    def __init__(self, element):
        self.element = element


class ElementChangeEvent(ElementEvent):
    """
    Generic event fired when element state changes.
    """

    def __init__(self, element, property):
        self.element = element
        self.property = property


@implementer(IAttributeChangeEvent)
class AttributeChangeEvent(ElementChangeEvent):
    """A UML attribute has changed value."""

    def __init__(self, element, attribute, old_value, new_value):
        """Constructor.  The element parameter is the element with the
        changing attribute.  The attribute parameter is the parameter
        element that changed.  The old_value is the old value of the attribute
        and the new_value is the new value of the attribute."""

        super().__init__(element, attribute)
        self.old_value = old_value
        self.new_value = new_value


@implementer(IAssociationChangeEvent)
class AssociationChangeEvent(ElementChangeEvent):
    """An association UML element has changed."""

    def __init__(self, element, association):
        """Constructor.  The element parameter is the element the association
        is changing from.  The association parameter is the changed
        association element."""

        super().__init__(element, association)


@implementer(IAssociationSetEvent)
class AssociationSetEvent(AssociationChangeEvent):
    """An association element has been set."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element setting the
        association element.  The association parameter is the association
        element being set.  The old_value parameter is the old association
        and the new_value parameter is the new association."""

        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


@implementer(IAssociationAddEvent)
class AssociationAddEvent(AssociationChangeEvent):
    """An association element has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element the association
        has been added to.  The association parameter is the association
        element being added."""

        AssociationChangeEvent.__init__(self, element, association)
        self.new_value = new_value


@implementer(IAssociationDeleteEvent)
class AssociationDeleteEvent(AssociationChangeEvent):
    """An association element has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element the association
        has been deleted from.  The association parameter is the deleted
        association element."""

        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value


class DerivedChangeEvent(AssociationChangeEvent):
    """A derived property has changed."""

    pass


@implementer(IAssociationSetEvent)
class DerivedSetEvent(DerivedChangeEvent, AssociationSetEvent):
    """A generic derived set event."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element to which the
        derived set belongs.  The association parameter is the association
        of the derived set."""

        super().__init__(element, association, old_value, new_value)


@implementer(IAssociationAddEvent)
class DerivedAddEvent(DerivedChangeEvent, AssociationAddEvent):
    """A derived property has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element to which the
        derived property belongs.  The association parameter is the
        association of the derived property."""

        super().__init__(element, association, new_value)


@implementer(IAssociationDeleteEvent)
class DerivedDeleteEvent(DerivedChangeEvent, AssociationDeleteEvent):
    """A derived property has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element to which the
        derived property belongs.  The association parameter is the
        association of the derived property."""

        super().__init__(element, association, old_value)


@implementer(IAssociationSetEvent)
class RedefineSetEvent(AssociationSetEvent):
    """A redefined property has been set."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is association of the
        property."""

        super().__init__(element, association, old_value, new_value)


@implementer(IAssociationAddEvent)
class RedefineAddEvent(AssociationAddEvent):
    """A redefined property has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is the association of
        the property."""

        super().__init__(element, association, new_value)


@implementer(IAssociationDeleteEvent)
class RedefineDeleteEvent(AssociationDeleteEvent):
    """A redefined property has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is the association of
        the property."""

        super().__init__(element, association, old_value)


class ElementFactoryEvent(ServiceEvent):
    """Events originated from the Elementfactory service."""

    def __init__(self, service):
        self.service = service


class ElementCreateEvent(ElementFactoryEvent):
    """An element has been created."""

    def __init__(self, service, element):
        """Constructor.  The service parameter is the service responsible
        for creating the element.  The element parameter is the element being
        created."""
        super().__init__(service)
        self.element = element


class DiagramItemCreateEvent(ElementCreateEvent):
    """A diagram item has been created."""

    def __init__(self, service, element):
        """Constructor.  The element parameter is the element being created."""
        super().__init__(service, element)


class ElementDeleteEvent(ElementFactoryEvent):
    """An element has been deleted."""

    def __init__(self, service, element):
        """Constructor.  The service parameter is the service responsible for
        deleting the element.  The element parameter is the element being
        deleted."""
        super().__init__(service)
        self.element = element


class ModelFactoryEvent(ElementFactoryEvent):
    """A generic element factory event."""

    def __init__(self, service):
        """Constructor.  The service parameter is the service the emitted the
        event."""
        super().__init__(service)


class FlushFactoryEvent(ElementFactoryEvent):
    """The element factory has been flushed."""

    def __init__(self, service):
        """Constructor.  The service parameter is the service responsible for
        flushing the factory."""
        super().__init__(service)
