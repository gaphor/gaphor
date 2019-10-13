"""The core UML metamodel events."""

from gaphor.event import ServiceEvent


class ElementUpdated:
    """
    Generic event fired when element state changes.
    """

    def __init__(self, element, property):
        self.element = element
        self.property = property


class AttributeUpdated(ElementUpdated):
    """A UML attribute has changed value."""

    def __init__(self, element, attribute, old_value, new_value):
        """Constructor.  The element parameter is the element with the
        changing attribute.  The attribute parameter is the parameter
        element that changed.  The old_value is the old value of the attribute
        and the new_value is the new value of the attribute."""

        super().__init__(element, attribute)
        self.old_value = old_value
        self.new_value = new_value


class AssociationUpdated(ElementUpdated):
    """An association UML element has changed."""

    def __init__(self, element, association):
        """Constructor.  The element parameter is the element the association
        is changing from.  The association parameter is the changed
        association element."""

        super().__init__(element, association)


class AssociationSet(AssociationUpdated):
    """An association element has been set."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element setting the
        association element.  The association parameter is the association
        element being set.  The old_value parameter is the old association
        and the new_value parameter is the new association."""

        AssociationUpdated.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


class AssociationAdded(AssociationUpdated):
    """An association element has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element the association
        has been added to.  The association parameter is the association
        element being added."""

        AssociationUpdated.__init__(self, element, association)
        self.new_value = new_value


class AssociationDeleted(AssociationUpdated):
    """An association element has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element the association
        has been deleted from.  The association parameter is the deleted
        association element."""

        AssociationUpdated.__init__(self, element, association)
        self.old_value = old_value


class DerivedUpdated(AssociationUpdated):
    """A derived property has changed."""


class DerivedSet(AssociationSet, DerivedUpdated):
    """A generic derived set event."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element to which the
        derived set belongs.  The association parameter is the association
        of the derived set."""

        super().__init__(element, association, old_value, new_value)


class DerivedAdded(AssociationAdded, DerivedUpdated):
    """A derived property has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element to which the
        derived property belongs.  The association parameter is the
        association of the derived property."""

        super().__init__(element, association, new_value)


class DerivedDeleted(AssociationDeleted, DerivedUpdated):
    """A derived property has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element to which the
        derived property belongs.  The association parameter is the
        association of the derived property."""

        super().__init__(element, association, old_value)


class RedefinedSet(AssociationSet):
    """A redefined property has been set."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is association of the
        property."""

        super().__init__(element, association, old_value, new_value)


class RedefinedAdded(AssociationAdded):
    """A redefined property has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is the association of
        the property."""

        super().__init__(element, association, new_value)


class RedefinedDeleted(AssociationDeleted):
    """A redefined property has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is the association of
        the property."""

        super().__init__(element, association, old_value)


class ElementCreated(ServiceEvent):
    """An element has been created."""

    def __init__(self, service, element):
        """Constructor.  The service parameter is the service responsible
        for creating the element.  The element parameter is the element being
        created."""
        super().__init__(service)
        self.element = element


class DiagramItemCreated(ElementCreated):
    """A diagram item has been created."""

    def __init__(self, service, element):
        """Constructor.  The element parameter is the element being created."""
        super().__init__(service, element)


class ElementDeleted(ServiceEvent):
    """An element has been deleted."""

    def __init__(self, service, element):
        """Constructor.  The service parameter is the service responsible for
        deleting the element.  The element parameter is the element being
        deleted."""
        super().__init__(service)
        self.element = element


class ModelReady(ServiceEvent):
    """A generic element factory event."""

    def __init__(self, service):
        """Constructor.  The service parameter is the service the emitted the
        event."""
        super().__init__(service)


class ModelFlushed(ServiceEvent):
    """The element factory has been flushed."""

    def __init__(self, service):
        """Constructor.  The service parameter is the service responsible for
        flushing the factory."""
        super().__init__(service)
