"""
Properties used to create the UML 2.0 data model.

The logic for creating and destroying connections between UML objects is
implemented in Python property classes. These classes are simply instantiated
like this:
    class Class(Element): pass
    class Comment(Element): pass
    Class.ownedComment = association('ownedComment', Comment,
                                     0, '*', 'annotatedElement')
    Comment.annotatedElement = association('annotatedElement', Element,
                                           0, '*', 'ownedComment')

Same for attributes and enumerations.

Each property type (association, attribute and enumeration) has three specific
methods:
    _get():           return the value
    _set(value):      set the value or add it to a list
    _del(value=None): delete the value. 'value' is used to tell which value
                      is to be removed (in case of associations with
                      multiplicity > 1).
    load(value):      load 'value' as the current value for this property
    save(save_func):  send the value of the property to save_func(name, value)
"""

__all__ = ["attribute", "enumeration", "association", "derivedunion", "redefine"]

import logging

from zope import component

from gaphor.UML.collection import collection, collectionlist
from gaphor.UML.event import AssociationAddEvent, AssociationDeleteEvent
from gaphor.UML.event import AttributeChangeEvent, AssociationSetEvent
from gaphor.UML.event import DerivedAddEvent, DerivedDeleteEvent
from gaphor.UML.event import DerivedChangeEvent, DerivedSetEvent
from gaphor.UML.event import RedefineSetEvent, RedefineAddEvent, RedefineDeleteEvent
from gaphor.UML.interfaces import IAssociationDeleteEvent
from gaphor.UML.interfaces import IAssociationSetEvent, IAssociationAddEvent
from gaphor.UML.interfaces import IElementChangeEvent, IAssociationChangeEvent


log = logging.getLogger(__name__)


class umlproperty(object):
    """
    Superclass for attribute, enumeration and association.

    The subclasses should define a ``name`` attribute that contains the name
    of the property. Derived properties (derivedunion and redefine) can be
    connected, they will be notified when the value changes.

    In some cases properties call out and delegate actions to the ElementFactory,
    for example in the case of event handling.
    """

    def __get__(self, obj, class_=None):
        if obj:
            return self._get(obj)
        return self

    def __set__(self, obj, value):
        self._set(obj, value)

    def __delete__(self, obj, value=None):
        self._del(obj, value)

    def save(self, obj, save_func):
        if hasattr(obj, self._name):
            save_func(self.name, self._get(obj))

    def load(self, obj, value):
        self._set(obj, value)

    def postload(self, obj):
        pass

    def unlink(self, obj):
        """
        This is called from the Element to denote the element is unlinking.
        """
        pass

    def handle(self, event):
        factory = event.element.factory
        if factory:
            factory._handle(event)
        else:
            component.handle(event)


class attribute(umlproperty):
    """
    Attribute.

    Element.attr = attribute('attr', types.StringType, '')
    """

    # TODO: check if lower and upper are actually needed for attributes
    def __init__(self, name, type, default=None, lower=0, upper=1):
        self.name = name
        self._name = "_" + name
        self.type = type
        self.default = default
        self.lower = lower
        self.upper = upper

    def load(self, obj, value):

        """Load the attribute value."""

        try:

            setattr(obj, self._name, self.type(value))

        except ValueError:

            error_msg = "Failed to load attribute %s of type %s with value %s" % (
                self._name,
                self.type,
                value,
            )

            raise TypeError(error_msg)

    def __str__(self):
        if self.lower == self.upper:
            return "<attribute %s: %s[%s] = %s>" % (
                self.name,
                self.type,
                self.lower,
                self.default,
            )
        else:
            return "<attribute %s: %s[%s..%s] = %s>" % (
                self.name,
                self.type,
                self.lower,
                self.upper,
                self.default,
            )

    def _get(self, obj):
        try:
            return getattr(obj, self._name)
        except AttributeError:
            return self.default

    def _set(self, obj, value):
        if value is not None:
            if not isinstance(value, self.type) and not isinstance(value, str):
                raise AttributeError(
                    "Value should be of type %s" % hasattr(self.type, "__name__")
                    and self.type.__name__
                    or self.type
                )

        if value == self._get(obj):
            return

        # undoattributeaction(self, obj, self._get(obj))

        old = self._get(obj)
        if value == self.default and hasattr(obj, self._name):
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.handle(AttributeChangeEvent(obj, self, old, value))

    def _del(self, obj, value=None):
        old = self._get(obj)
        try:
            # undoattributeaction(self, obj, self._get(obj))
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.handle(AttributeChangeEvent(obj, self, old, self.default))


class enumeration(umlproperty):
    """
    Enumeration

      Element.enum = enumeration('enum', ('one', 'two', 'three'), 'one')

    An enumeration is a special kind of attribute that can only hold a
    predefined set of values. Multiplicity is always `[0..1]`
    """

    # All enumerations have a type 'str'
    type = property(lambda s: str)

    def __init__(self, name, values, default):
        self.name = name
        self._name = "_" + name
        self.values = values
        self.default = default
        self.lower = 0
        self.upper = 1

    def __str__(self):
        return "<enumeration %s: %s = %s>" % (self.name, self.values, self.default)

    def _get(self, obj):
        try:
            return getattr(obj, self._name)
        except AttributeError:
            return self.default

    def load(self, obj, value):
        if not value in self.values:
            raise AttributeError("Value should be one of %s" % str(self.values))
        setattr(obj, self._name, value)

    def _set(self, obj, value):
        if not value in self.values:
            raise AttributeError("Value should be one of %s" % str(self.values))
        old = self._get(obj)
        if value == old:
            return

        if value == self.default:
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.handle(AttributeChangeEvent(obj, self, old, value))

    def _del(self, obj, value=None):
        old = self._get(obj)
        try:
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.handle(AttributeChangeEvent(obj, self, old, self.default))


class association(umlproperty):
    """
    Association, both uni- and bi-directional.

    Element.assoc = association('assoc', Element, opposite='other')
    
    A listerer is connected to the value added to the association. This
    will cause the association to be ended if the element on the other end
    of the association is unlinked.

    If the association is a composite relationship, the association will
    unlink all elements attached to if it is unlinked.
    """

    def __init__(self, name, type, lower=0, upper="*", composite=False, opposite=None):
        self.name = name
        self._name = "_" + name
        self.type = type
        self.lower = lower
        self.upper = upper
        self.composite = composite
        self.opposite = opposite and opposite
        self.stub = None

    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError(
                "Value for %s should be of type %s (%s)"
                % (self.name, self.type.__name__, type(value).__name__)
            )
        self._set(obj, value, do_notify=False)

    def postload(self, obj):
        """
        In the postload step, ensure that bi-directional associations
        are bi-directional.
        """
        values = self._get(obj)
        if not values:
            return
        if self.upper == 1:
            values = [values]
        for value in values:
            if not isinstance(value, self.type):
                raise AttributeError(
                    "Error in postload validation for %s: Value %s should be of type %s"
                    % (self.name, value, self.type.__name__)
                )

    def __str__(self):
        if self.lower == self.upper:
            s = "<association %s: %s[%s]" % (self.name, self.type.__name__, self.lower)
        else:
            s = "<association %s: %s[%s..%s]" % (
                self.name,
                self.type.__name__,
                self.lower,
                self.upper,
            )
        if self.opposite:
            s += " %s-> %s" % (self.composite and "<>" or "", self.opposite)
        return s + ">"

    def _get(self, obj):
        # TODO: Handle lower and add items if lower > 0
        try:
            return getattr(obj, self._name)
        except AttributeError:
            if self.upper == 1:
                return None
            else:
                # Create the empty collection here since it might be used to
                # add
                c = collection(self, obj, self.type)
                setattr(obj, self._name, c)
                return c

    def _set(self, obj, value, from_opposite=False, do_notify=True):
        """
        Set a new value for our attribute. If this is a collection, append
        to the existing collection.

        This method is called from the opposite association property.
        """
        if not (isinstance(value, self.type) or (value is None and self.upper == 1)):
            raise AttributeError("Value should be of type %s" % self.type.__name__)
        # Remove old value only for uni-directional associations
        if self.upper == 1:
            old = self._get(obj)

            # do nothing if we are assigned our current value:
            # Still do your thing, since undo handlers expect that.
            if value is old:
                return

            if old:
                self._del(obj, old, from_opposite=from_opposite, do_notify=False)

            if do_notify:
                event = AssociationSetEvent(obj, self, old, value)

            if value is None:
                if do_notify:
                    self.handle(event)
                return

            setattr(obj, self._name, value)

        else:
            # Set the actual value
            c = self._get(obj)
            if not c:
                c = collection(self, obj, self.type)
                setattr(obj, self._name, c)
            elif value in c:
                return

            c.items.append(value)
            if do_notify:
                event = AssociationAddEvent(obj, self, value)

        if not from_opposite and self.opposite:
            opposite = getattr(type(value), self.opposite)
            if not opposite.opposite:
                opposite.stub = self
            opposite._set(value, obj, from_opposite=True, do_notify=do_notify)
        elif not self.opposite:
            if not self.stub:
                self.stub = associationstub(self)
                setattr(self.type, "UML_associationstub_%x" % id(self), self.stub)
            self.stub._set(value, obj)

        if do_notify:
            self.handle(event)

    def _del(self, obj, value, from_opposite=False, do_notify=True):
        """
        Delete is used for element deletion and for removal of
        elements from a list.

        """
        if not value:
            if self.upper != "*" and self.upper > 1:
                raise Exception("Can not delete collections")
            old = value = self._get(obj)
            if value is None:
                return

        if not from_opposite and self.opposite:
            getattr(type(value), self.opposite)._del(value, obj, from_opposite=True)
        elif not self.opposite:
            if self.stub:
                self.stub._del(value, obj, from_opposite=True)

        event = None
        if self.upper == 1:
            try:
                delattr(obj, self._name)
            except:
                pass
            else:
                if do_notify:
                    event = AssociationSetEvent(obj, self, value, None)
        else:
            c = self._get(obj)
            if c:
                items = c.items
                try:
                    items.remove(value)
                except:
                    pass
                else:
                    if do_notify:
                        event = AssociationDeleteEvent(obj, self, value)

                # Remove items collection if empty
                if not items:
                    delattr(obj, self._name)

        if do_notify and event:
            self.handle(event)

    def unlink(self, obj):
        values = self._get(obj)
        composite = self.composite
        if values:
            if self.upper == 1:
                values = [values]

            for value in list(values):
                # TODO: make normal unlinking work through this method.
                self.__delete__(obj, value)
                if composite:
                    value.unlink()


class AssociationStubError(Exception):
    pass


class associationstub(umlproperty):
    """
    An association stub is an internal thingy that ensures all associations
    are always bi-directional. This helps the application when one end of
    the association is unlinked. On unlink() of an element all `umlproperty`'s
    are iterated and called by their unlink() method.
    """

    def __init__(self, association):
        self.association = association
        self._name = "_stub_%x" % id(self)

    def __get__(self, obj, class_=None):
        if obj:
            raise AssociationStubError("getting values not allowed")
        return self

    def __set__(self, obj, value):
        raise AssociationStubError("setting values not allowed")

    def __delete__(self, obj, value=None):
        raise AssociationStubError("deleting values not allowed")

    def save(self, obj, save_func):
        pass

    def load(self, obj, value):
        pass

    def unlink(self, obj):
        try:
            values = getattr(obj, self._name)
        except AttributeError:
            pass
        else:
            for value in set(values):
                self.association.__delete__(value, obj)

    def _set(self, obj, value):
        try:
            getattr(obj, self._name).add(value)
        except AttributeError:
            setattr(obj, self._name, set([value]))

    def _del(self, obj, value, from_opposite=False):
        try:
            c = getattr(obj, self._name)
        except AttributeError:
            pass
        else:
            c.discard(value)


class unioncache(object):
    """
    Small cache helper object for derivedunions.
    """

    def __init__(self, data, version):
        self.data = data
        self.version = version


class derived(umlproperty):
    """
    Base class for derived properties, both derived unions and custom
    properties.

    Note that, although this derived property sends DerivedAddEvent,
    -Delete- and Set events, this gives just an assumption that something
    may have changed. If something actually changed depends on the filter
    applied to the derived property.
    """

    def __init__(self, name, type, lower, upper, *subsets):
        self.name = name
        self._name = "_" + name
        self.version = 1
        self.type = type
        self.lower = lower
        self.upper = upper
        self.subsets = set(subsets)
        self.single = len(subsets) == 1

        component.provideHandler(self._association_changed)

    def load(self, obj, value):
        raise ValueError(
            "Derivedunion: Properties should not be loaded in a derived union %s: %s"
            % (self.name, value)
        )

    def postload(self, obj):
        self.version += 1

    def save(self, obj, save_func):
        pass

    def __str__(self):
        return "<derived %s: %s>" % (self.name, str(list(map(str, self.subsets)))[1:-1])

    def filter(self, obj):
        """
        Filter should return something iterable.
        """
        raise NotImplementedError("Implement this in the property.")

    def _update(self, obj):
        """
        Update the list of items. Returns a unioncache instance.
        """
        u = self.filter(obj)
        if self.upper != "*" and self.upper <= 1:
            assert len(u) <= 1, (
                "Derived union %s of item %s should have length 1 %s"
                % (self.name, obj.id, tuple(u))
            )
            # maybe code below is better instead the assertion above?
            # if len(u) > 1:
            #    log.warning('Derived union %s of item %s should have length 1 %s' % (self.name, obj.id, tuple(u)))
            if u:
                u = next(iter(u))
            else:
                u = None

        uc = unioncache(u, self.version)
        setattr(obj, self._name, uc)
        return uc

    def _get(self, obj):
        try:
            uc = getattr(obj, self._name)
            if uc.version != self.version:
                uc = self._update(obj)
        except AttributeError:
            uc = self._update(obj)

        return uc.data

    def _set(self, obj, value):
        raise AttributeError("Can not set values on a union")

    def _del(self, obj, value=None):
        raise AttributeError("Can not delete values on a union")

    @component.adapter(IElementChangeEvent)
    def _association_changed(self, event):
        """
        Re-emit state change for the derived properties as Derived*Event's.

        TODO: We should fetch the old and new state of the namespace item in
        stead of the old and new values of the item that changed.

        If multiplicity is [0..1]:
          send DerivedSetEvent if len(union) < 2
        if multiplicity is [*]:
          send DerivedAddEvent and DerivedDeleteEvent
            if value not in derived union and 
        """
        if event.property in self.subsets:
            # Make sure unions are created again
            self.version += 1

            if not IAssociationChangeEvent.providedBy(event):
                return

            # mimic the events for Set/Add/Delete
            if self.upper == 1:
                # This is a [0..1] event
                # TODO: This is an error: [0..*] associations may be used for updating [0..1] associations
                assert IAssociationSetEvent.providedBy(event)
                old_value, new_value = event.old_value, event.new_value
                self.handle(DerivedSetEvent(event.element, self, old_value, new_value))
            else:
                if IAssociationSetEvent.providedBy(event):
                    old_value, new_value = event.old_value, event.new_value
                    # Do a filter? Change to
                    self.handle(DerivedDeleteEvent(event.element, self, old_value))
                    self.handle(DerivedAddEvent(event.element, self, new_value))

                elif IAssociationAddEvent.providedBy(event):
                    new_value = event.new_value
                    self.handle(DerivedAddEvent(event.element, self, new_value))

                elif IAssociationDeleteEvent.providedBy(event):
                    old_value = event.old_value
                    self.handle(DerivedDeleteEvent(event.element, self, old_value))

                elif IAssociationChangeEvent.providedBy(event):
                    self.handle(DerivedChangeEvent(event.element, self))
                else:
                    log.error(
                        "Don"
                        "t know how to handle event "
                        + str(event)
                        + " for derived union"
                    )


class derivedunion(derived):
    """
    Derived union

      Element.union = derivedunion('union', subset1, subset2..subsetn)

    The subsets are the properties that participate in the union (Element.name).
    """

    def _union(self, obj, exclude=None):
        """
        Returns a union of all values as a set.
        """
        if self.single:
            return next(iter(self.subsets)).__get__(obj)
        else:
            u = set()
            for s in self.subsets:
                if s is exclude:
                    continue
                tmp = s.__get__(obj)
                if tmp:
                    try:
                        u.update(tmp)
                    except TypeError:
                        # [0..1] property
                        u.add(tmp)
            return collectionlist(u)

    # Filter is our default filter
    filter = _union

    @component.adapter(IElementChangeEvent)
    def _association_changed(self, event):
        """
        Re-emit state change for the derived union (as Derived*Event's).

        TODO: We should fetch the old and new state of the namespace item in
        stead of the old and new values of the item that changed.

        If multiplicity is [0..1]:
          send DerivedSetEvent if len(union) < 2
        if multiplicity is [*]:
          send DerivedAddEvent and DerivedDeleteEvent
            if value not in derived union and 
        """
        if event.property in self.subsets:
            # Make sure unions are created again
            self.version += 1

            if not IAssociationChangeEvent.providedBy(event):
                return

            values = self._union(event.element, exclude=event.property)

            if self.upper == 1:
                assert IAssociationSetEvent.providedBy(event)
                old_value, new_value = event.old_value, event.new_value
                # This is a [0..1] event
                if self.single:
                    # Only one subset element, so pass the values on
                    self.handle(
                        DerivedSetEvent(event.element, self, old_value, new_value)
                    )
                else:
                    new_values = set(values)
                    if new_value:
                        new_values.add(new_value)
                    if len(new_values) > 1:
                        # In an in-between state. Do not emit notifications
                        return
                    if values:
                        new_value = next(iter(values))
                    self.handle(
                        DerivedSetEvent(event.element, self, old_value, new_value)
                    )
            else:
                if IAssociationSetEvent.providedBy(event):
                    old_value, new_value = event.old_value, event.new_value
                    if old_value and old_value not in values:
                        self.handle(DerivedDeleteEvent(event.element, self, old_value))
                    if new_value and new_value not in values:
                        self.handle(DerivedAddEvent(event.element, self, new_value))

                elif IAssociationAddEvent.providedBy(event):
                    new_value = event.new_value
                    if new_value not in values:
                        self.handle(DerivedAddEvent(event.element, self, new_value))

                elif IAssociationDeleteEvent.providedBy(event):
                    old_value = event.old_value
                    if old_value not in values:
                        self.handle(DerivedDeleteEvent(event.element, self, old_value))

                elif IAssociationChangeEvent.providedBy(event):
                    self.handle(DerivedChangeEvent(event.element, self))
                else:
                    log.error(
                        "Don"
                        "t know how to handle event "
                        + str(event)
                        + " for derived union"
                    )


class redefine(umlproperty):
    """
    Redefined association

      Element.redefine = redefine(Element, 'redefine', Class, Element.assoc)

    If the redefine eclipses the original property (it has the same name)
    it ensures that the original values are saved and restored.
    """

    def __init__(self, decl_class, name, type, original):
        self.decl_class = decl_class
        self.name = name
        self._name = "_" + name
        self.type = type
        self.original = original

        component.provideHandler(self._association_changed)

    upper = property(lambda s: s.original.upper)
    lower = property(lambda s: s.original.lower)
    opposite = property(lambda s: s.original.opposite)

    def load(self, obj, value):
        if self.original.name == self.name:
            self.original.load(obj, value)

    def postload(self, obj):
        if self.original.name == self.name:
            self.original.postload(obj)

    def save(self, obj, save_func):
        if self.original.name == self.name:
            self.original.save(obj, save_func)

    def unlink(self, obj):
        if self.original.name == self.name:
            self.original.unlink(obj)

    def __str__(self):
        return "<redefine %s: %s = %s>" % (
            self.name,
            self.type.__name__,
            str(self.original),
        )

    def __get__(self, obj, class_=None):
        # No longer needed
        if not obj:
            return self
        return self.original.__get__(obj, class_)

    def __set__(self, obj, value):
        # No longer needed
        if not isinstance(value, self.type):
            raise AttributeError("Value should be of type %s" % self.type.__name__)
        self.original.__set__(obj, value)

    def __delete__(self, obj, value=None):
        # No longer needed
        self.original.__delete__(obj, value)

    def _get(self, obj):
        return self.original._get(obj)

    def _set(self, obj, value, from_opposite=False):
        return self.original._set(obj, value, from_opposite)

    def _del(self, obj, value, from_opposite=False):
        return self.original._del(obj, value, from_opposite)

    @component.adapter(IAssociationChangeEvent)
    def _association_changed(self, event):
        if event.property is self.original and isinstance(
            event.element, self.decl_class
        ):
            # mimic the events for Set/Add/Delete
            if IAssociationSetEvent.providedBy(event):
                self.handle(
                    RedefineSetEvent(
                        event.element, self, event.old_value, event.new_value
                    )
                )
            elif IAssociationAddEvent.providedBy(event):
                self.handle(RedefineAddEvent(event.element, self, event.new_value))
            elif IAssociationDeleteEvent.providedBy(event):
                self.handle(RedefineDeleteEvent(event.element, self, event.old_value))
            else:
                log.error(
                    "Don"
                    "t know how to handle event "
                    + str(event)
                    + " for redefined association"
                )


try:
    import psyco
except ImportError:
    pass
else:
    psyco.bind(umlproperty)
    psyco.bind(attribute)
    psyco.bind(enumeration)
    psyco.bind(association)
    psyco.bind(derivedunion)
    psyco.bind(redefine)
