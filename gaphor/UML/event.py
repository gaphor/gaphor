"""The core UML metamodel events."""

from gaphor.UML.interfaces import *
from zope.interface import implementer


@implementer(IAttributeChangeEvent)
class AttributeChangeEvent(object):
    """A UML attribute has changed value."""

    def __init__(self, element, attribute, old_value, new_value):
        """Constructor.  The element parameter is the element with the
        changing attribute.  The attribute parameter is the parameter
        element that changed.  The old_value is the old value of the attribute
        and the new_value is the new value of the attribute."""
        
        self.element = element
        self.property = attribute
        self.old_value = old_value
        self.new_value = new_value


@implementer(IAssociationChangeEvent)
class AssociationChangeEvent(object):
    """An association UML element has changed."""
    
    def __init__(self, element, association):
        """Constructor.  The element parameter is the element the association
        is changing from.  The association parameter is the changed
        association element."""
        
        self.element = element
        self.property = association


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
class DerivedSetEvent(DerivedChangeEvent):
    """A generic derived set event."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element to which the
        derived set belongs.  The association parameter is the association
        of the derived set."""
        
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


@implementer(IAssociationAddEvent)
class DerivedAddEvent(DerivedChangeEvent):
    """A derived property has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element to which the
        derived property belongs.  The association parameter is the 
        association of the derived property."""
        
        AssociationChangeEvent.__init__(self, element, association)
        self.new_value = new_value


@implementer(IAssociationDeleteEvent)
class DerivedDeleteEvent(DerivedChangeEvent):
    """A derived property has been deleted."""

    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element to which the
        derived property belongs.  The association parameter is the 
        association of the derived property."""
        
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value


@implementer(IAssociationSetEvent)
class RedefineSetEvent(AssociationChangeEvent):
    """A redefined property has been set."""

    def __init__(self, element, association, old_value, new_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is association of the 
        property."""
        
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value
        self.new_value = new_value


@implementer(IAssociationAddEvent)
class RedefineAddEvent(AssociationChangeEvent):
    """A redefined property has been added."""

    def __init__(self, element, association, new_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is the association of
        the property."""
        
        AssociationChangeEvent.__init__(self, element, association)
        self.new_value = new_value


@implementer(IAssociationDeleteEvent)
class RedefineDeleteEvent(AssociationChangeEvent):
    """A redefined property has been deleted."""
    
    def __init__(self, element, association, old_value):
        """Constructor.  The element parameter is the element to which the
        property belongs.  The association parameter is the association of
        the property."""
        
        AssociationChangeEvent.__init__(self, element, association)
        self.old_value = old_value


@implementer(IElementCreateEvent)
class DiagramItemCreateEvent(object):
    """A diagram item has been created."""
    
    def __init__(self, element):
        """Constructor.  The element parameter is the element being created."""
        
        self.element = element


@implementer(IElementCreateEvent, IElementFactoryEvent)
class ElementCreateEvent(object):
    """An element has been created."""
    
    def __init__(self, service, element):
        """Constructor.  The service parameter is the service responsible
        for creating the element.  The element parameter is the element being
        created."""
        
        self.service = service
        self.element = element


@implementer(IElementDeleteEvent, IElementFactoryEvent)
class ElementDeleteEvent(object):
    """An element has been deleted."""
    
    def __init__(self, service, element):
        """Constructor.  The service parameter is the service responsible for
        deleting the element.  The element parameter is the element being
        deleted."""
        
        self.service = service
        self.element = element


@implementer(IModelFactoryEvent)
class ModelFactoryEvent(object):
    """A generic element factory event."""

    def __init__(self, service):
        """Constructor.  The service parameter is the service the emitted the
        event."""
        
        self.service = service


@implementer(IFlushFactoryEvent)
class FlushFactoryEvent(object):
    """The element factory has been flushed."""

    def __init__(self, service):
        """Constructor.  The service parameter is the service responsible for
        flushing the factory."""
        
        self.service = service

