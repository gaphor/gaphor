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

from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    List,
    Optional,
    Sequence,
    Set,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import Literal, Protocol

from gaphor.UML.collection import collection, collectionlist
from gaphor.UML.event import (
    AssociationAdded,
    AssociationDeleted,
    AssociationSet,
    AssociationUpdated,
    AttributeUpdated,
    DerivedAdded,
    DerivedDeleted,
    DerivedSet,
    DerivedUpdated,
    ElementUpdated,
    RedefinedAdded,
    RedefinedDeleted,
    RedefinedSet,
)

__all__ = ["attribute", "enumeration", "association", "derivedunion", "redefine"]


if TYPE_CHECKING:
    from gaphor.UML.element import Element


log = logging.getLogger(__name__)


E = TypeVar("E")


class relation_one(Protocol[E]):

    name: str

    @overload
    def __get__(self, obj: None, class_=None) -> relation_one[E]:
        ...

    @overload  # noqa: F811
    def __get__(self, obj, class_=None) -> E:
        ...

    def __set__(self, obj, value: E) -> None:
        ...

    def __delete__(self, obj, value: E) -> None:
        ...


class relation_many(Protocol[E]):

    name: str

    @overload
    def __get__(self, obj: None, class_=None) -> relation_many[E]:
        ...

    @overload  # noqa: F811
    def __get__(self, obj, class_=None) -> collection[E]:
        ...

    def __set__(self, obj, value: E) -> None:
        ...

    def __delete__(self, obj, value: E) -> None:
        ...


relation = Union[relation_one, relation_many]

T = TypeVar("T")
A = TypeVar("A", int, str)

Lower = Union[Literal[0], Literal[1], Literal[2]]
Upper = Union[Literal[1], Literal["*"]]


class umlproperty(Generic[T]):
    """
    Superclass for attribute, enumeration and association.

    The subclasses should define a ``name`` attribute that contains the name
    of the property. Derived properties (derivedunion and redefine) can be
    connected, they will be notified when the value changes through
    `propagate(self, event)`.

    In some cases properties call out and delegate actions to the ElementFactory,
    for example, in the case of event handling.
    """

    lower: Lower = 0
    upper: Upper = 1

    def __init__(self, name: str):
        self._dependent_properties: Set[Union[derived, redefine]] = set()
        self.name = name
        self._name = "_" + name

    def __get__(self, obj, class_=None):
        if obj:
            return self._get(obj)
        return self

    def __set__(self, obj, value) -> None:
        self._set(obj, value)

    def __delete__(self, obj, value=None) -> None:
        self._del(obj, value)

    def save(self, obj, save_func: Callable[[str, object], None]):
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

    @overload
    def _get(self, obj: Literal[1]) -> Optional[T]:
        ...

    @overload  # noqa: F811
    def _get(self, obj: Literal["*"]) -> collection[T]:
        ...

    def _get(self, obj):  # noqa: F811
        raise NotImplementedError()

    def _set(self, obj, value: Optional[T]) -> None:
        raise NotImplementedError()

    def _del(self, obj, value: Optional[T]) -> None:
        raise NotImplementedError()

    def handle(self, event):
        event.element.handle(event)
        for d in self._dependent_properties:
            d.propagate(event)


class attribute(umlproperty[A]):
    """
    Attribute.

    Element.attr = attribute('attr', types.StringType, '')
    """

    # TODO: check if lower and upper are actually needed for attributes
    def __init__(
        self, name: str, type: Type[Union[str, int]], default: Optional[A] = None
    ):
        super().__init__(name)
        self.type = type
        self.default: Optional[A] = default

    def load(self, obj, value: str):
        """Load the attribute value."""
        try:
            setattr(obj, self._name, self.type(value))
        except ValueError:
            error_msg = "Failed to load attribute {} of type {} with value {}".format(
                self._name, self.type, value
            )
            raise TypeError(error_msg)

    def __str__(self):
        return f"<attribute {self.name}: {self.type} = {self.default}>"

    def _get(self, obj):
        try:
            v: Optional[A] = getattr(obj, self._name)
            return v
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

        old = self._get(obj)
        if value == self.default and hasattr(obj, self._name):
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.handle(AttributeUpdated(obj, self, old, value))

    def _del(self, obj, value=None):
        old = self._get(obj)
        try:
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.handle(AttributeUpdated(obj, self, old, self.default))


class enumeration(umlproperty[str]):
    """
    Enumeration

      Element.enum = enumeration('enum', ('one', 'two', 'three'), 'one')

    An enumeration is a special kind of attribute that can only hold a
    predefined set of values. Multiplicity is always `[0..1]`
    """

    # All enumerations have a type 'str'
    type = str

    def __init__(self, name: str, values: Sequence[str], default: str):
        super().__init__(name)
        self.values = values
        self.default = default

    def __str__(self):
        return f"<enumeration {self.name}: {self.values} = {self.default}>"

    def _get(self, obj):
        try:
            return getattr(obj, self._name)
        except AttributeError:
            return self.default

    def load(self, obj, value):
        if value not in self.values:
            raise AttributeError("Value should be one of %s" % str(self.values))
        setattr(obj, self._name, value)

    def _set(self, obj, value):
        if value not in self.values:
            raise AttributeError("Value should be one of %s" % str(self.values))
        old = self._get(obj)
        if value == old:
            return

        if value == self.default:
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.handle(AttributeUpdated(obj, self, old, value))

    def _del(self, obj, value=None):
        old = self._get(obj)
        try:
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.handle(AttributeUpdated(obj, self, old, self.default))


class association(umlproperty[T]):
    """
    Association, both uni- and bi-directional.

    Element.assoc = association('assoc', Element, opposite='other')

    A listerer is connected to the value added to the association. This
    will cause the association to be ended if the element on the other end
    of the association is unlinked.

    If the association is a composite relationship, the association will
    unlink all elements attached to if it is unlinked.
    """

    def __init__(
        self,
        name: str,
        type: Type,
        lower: Lower = 0,
        upper: Upper = "*",
        composite: bool = False,
        opposite: Optional[str] = None,
    ):
        super().__init__(name)
        self.type = type
        self.lower = lower
        self.upper = upper
        self.composite = composite
        self.opposite = opposite
        self.stub: Optional[associationstub] = None

    def load(self, obj, value):
        if not isinstance(value, self.type):
            raise AttributeError(
                "Value for %s should be of type %s (%s)"
                % (self.name, self.type.__name__, type(value).__name__)
            )
        self._set(obj, value, do_notify=False)

    def __str__(self):
        if self.lower == self.upper:
            s = f"<association {self.name}: {self.type.__name__}[{self.lower}]"
        else:
            s = f"<association {self.name}: {self.type.__name__}[{self.lower}..{self.upper}]"
        if self.opposite:
            s += f" {self.composite and '<>' or ''}-> {self.opposite}"
        return s + ">"

    def _get(self, obj):
        if self.upper == 1:
            return self._get_one(obj)
        else:
            return self._get_many(obj)

    def _get_one(self, obj) -> Optional[T]:
        v: Optional[T] = getattr(obj, self._name, None)
        return v

    def _get_many(self, obj) -> collection[T]:
        v: Optional[collection[T]] = getattr(obj, self._name, None)
        if v is None:
            # Create the empty collection here since it might
            # be used to add.
            v = collection(self, obj, self.type)
            setattr(obj, self._name, v)
        return v

    def _set(
        self, obj, value: Optional[T], from_opposite=False, do_notify=True
    ) -> None:
        """
        Set a new value for our attribute. If this is a collection, append
        to the existing collection.

        This method is called from the opposite association property.
        """
        if self.upper == 1:
            self._set_one(obj, value, from_opposite, do_notify)
        else:
            self._set_many(obj, value, from_opposite, do_notify)

    def _set_one(self, obj, value, from_opposite, do_notify) -> None:
        if not (isinstance(value, self.type) or (value is None)):
            raise AttributeError(f"Value should be of type {self.type.__name__}")

        old = self._get(obj)

        # do nothing if we are assigned our current value:
        # Still do your thing, since undo handlers expect that.
        if value is old:
            return

        if old:
            self._del(obj, old, from_opposite=from_opposite, do_notify=False)

        if value is not None:
            setattr(obj, self._name, value)
            self._set_opposite(obj, value, from_opposite, do_notify)

        if do_notify:
            self.handle(AssociationSet(obj, self, old, value))

    def _set_many(self, obj, value, from_opposite, do_notify) -> None:
        if not isinstance(value, self.type):
            raise AttributeError(f"Value should be of type {self.type.__name__}")

        # Set the actual value
        c = self._get_many(obj)
        if not c:
            c = collection(self, obj, self.type)
            setattr(obj, self._name, c)
        elif value in c:
            return

        c.items.append(value)
        self._set_opposite(obj, value, from_opposite, do_notify)

        if do_notify:
            self.handle(AssociationAdded(obj, self, value))

    def _set_opposite(
        self, obj, value: Optional[T], from_opposite=False, do_notify=True
    ) -> None:
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

    def _del(self, obj, value, from_opposite=False, do_notify=True):
        """
        Delete is used for element deletion and for removal of
        elements from a list.

        """
        if self.upper == 1:
            self._del_one(obj, value, from_opposite, do_notify)
        else:
            self._del_many(obj, value, from_opposite, do_notify)

    def _del_one(self, obj, value, from_opposite=False, do_notify=True):
        value = self._get_one(obj)
        if value is None:
            return

        self._del_opposite(obj, value, from_opposite)

        try:
            delattr(obj, self._name)
        except AttributeError:
            log.exception(f"Delete attribute failed for {obj} with {self._name}")
        else:
            if do_notify:
                self.handle(AssociationSet(obj, self, value, None))

    def _del_many(self, obj, value, from_opposite=False, do_notify=True):
        if not value:
            raise Exception("Can not delete collections")

        self._del_opposite(obj, value, from_opposite)

        c = self._get_many(obj)
        if c:
            items = c.items
            try:
                items.remove(value)
            except ValueError:
                log.exception(f"Removing {value} from list {items} failed")
            else:
                if do_notify:
                    self.handle(AssociationDeleted(obj, self, value))

            # Remove items collection if empty
            if not items:
                delattr(obj, self._name)

    def _del_opposite(self, obj, value, from_opposite):
        if not from_opposite and self.opposite:
            getattr(type(value), self.opposite)._del(value, obj, from_opposite=True)
        elif not self.opposite:
            if self.stub:
                self.stub._del(value, obj, from_opposite=True)

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


class associationstub(umlproperty[T]):
    """
    An association stub is an internal thingy that ensures all associations
    are always bi-directional. This helps the application when one end of
    the association is unlinked. On unlink() of an element all `umlproperty`'s
    are iterated and called by their unlink() method.
    """

    def __init__(self, association: association):
        super().__init__("stub_%x" % id(self))
        self.association = association

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
            log.exception(f"Failed to unlink {self._name} from {obj}")
        else:
            for value in set(values):
                self.association.__delete__(value, obj)

    def _set(self, obj, value):
        try:
            getattr(obj, self._name).add(value)
        except AttributeError:
            setattr(obj, self._name, {value})

    def _del(self, obj, value, from_opposite=False):
        try:
            c = getattr(obj, self._name)
        except AttributeError:
            pass
        else:
            c.discard(value)


class unioncache:
    """
    Small cache helper object for derivedunions.
    """

    def __init__(self, data: object, version: int) -> None:
        self.data = data
        self.version = version


class derived(umlproperty[T]):
    """
    Base class for derived properties, both derived unions and custom
    properties.

    Note that, although this derived property sends DerivedAdded,
    -Delete- and Set events, this gives just an assumption that something
    may have changed. If something actually changed depends on the filter
    applied to the derived property.

    NB. filter returns a *list* of filtered items, even when upper bound is 1.
    """

    opposite = None

    def __init__(
        self,
        decl_class: Type[E],
        name: str,
        type: Type[T],
        lower: Lower,
        upper: Upper,
        filter: Callable[[E], List[T]],
        *subsets: relation,
    ) -> None:
        super().__init__(name)
        self.version = 1
        self.type = type
        self.lower = lower
        self.upper = upper
        self.filter = filter
        self.subsets = set(subsets)
        self.single = len(subsets) == 1

        for s in subsets:
            assert isinstance(
                s, (association, derived)
            ), f"have element {s}, expected association"
            s._dependent_properties.add(self)

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
        return f"<derived {self.name}: {str(list(map(str, self.subsets)))[1:-1]}>"

    def _update(self, obj):
        """
        Update the list of items. Returns a unioncache instance.
        """
        u = self.filter(obj)
        if self.upper == 1:
            assert len(u) <= 1, (
                "Derived union %s of item %s should have length 1 %s"
                % (self.name, obj.id, tuple(u))
            )
            uc = unioncache(u[0] if u else None, self.version)
        else:
            uc = unioncache(u, self.version)
        setattr(obj, self._name, uc)
        return uc

    def _get(self, obj):
        if self.subsets:
            try:
                uc = getattr(obj, self._name)
                if uc.version != self.version:
                    uc = self._update(obj)
            except AttributeError:
                uc = self._update(obj)
        else:
            uc = self._update(obj)

        return uc.data

    def _set(self, obj, value):
        raise AttributeError("Can not set values on a union")

    def _del(self, obj, value=None):
        raise AttributeError("Can not delete values on a union")

    def propagate(self, event):
        """
        Re-emit state change for the derived properties as Derived*Event's.

        TODO: We should fetch the old and new state of the namespace item in
        stead of the old and new values of the item that changed.

        If multiplicity is [0..1]:
          send DerivedSet if len(union) < 2
        if multiplicity is [*]:
          send DerivedAdded and DerivedDeleted
            if value not in derived union and
        """
        if event.property in self.subsets:

            if not isinstance(event, AssociationUpdated):
                return

            # mimic the events for Set/Add/Delete
            if self.upper == 1:
                # This is a [0..1] event
                # TODO: This is an error: [0..*] associations may be used for updating [0..1] associations
                # assert isinstance(
                #     event, AssociationSet
                # ), f"Can only handle [0..1] set-events, not {event} for {event.element}"
                old_value = self._get(event.element)
                # Make sure unions are created again
                self.version += 1
                new_value = self._get(event.element)
                if old_value != new_value:
                    self.handle(DerivedSet(event.element, self, old_value, new_value))
            else:
                # Make sure unions are created again
                self.version += 1

                if isinstance(event, AssociationSet):
                    self.handle(DerivedDeleted(event.element, self, event.old_value))
                    self.handle(DerivedAdded(event.element, self, event.new_value))

                elif isinstance(event, AssociationAdded):
                    self.handle(DerivedAdded(event.element, self, event.new_value))

                elif isinstance(event, AssociationDeleted):
                    self.handle(DerivedDeleted(event.element, self, event.old_value))

                elif isinstance(event, AssociationUpdated):
                    self.handle(DerivedUpdated(event.element, self))
                else:
                    log.error(
                        "Don't know how to handle event "
                        + str(event)
                        + " for derived union"
                    )


class derivedunion(derived[T]):
    """
    Derived union

      Element.union = derivedunion('union', subset1, subset2..subsetn)

    The subsets are the properties that participate in the union (Element.name).
    """

    def __init__(
        self,
        decl_class: Type[E],
        name: str,
        type: Type[T],
        lower: Lower,
        upper: Upper,
        *subsets: relation,
    ):
        super().__init__(decl_class, name, type, lower, upper, self._union, *subsets)

    def _union(self, obj, exclude=None):
        """
        Returns a union of all values as a set.
        """
        if self.single:
            return next(iter(self.subsets)).__get__(obj)
        else:
            u: Set[T] = set()
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

    def propagate(self, event):
        """
        Re-emit state change for the derived union (as Derived*Event's).

        TODO: We should fetch the old and new state of the namespace item in
        stead of the old and new values of the item that changed.

        If multiplicity is [0..1]:
          send DerivedSet if len(union) < 2
        if multiplicity is [*]:
          send DerivedAdded and DerivedDeleted
            if value not in derived union and
        """
        if event.property in self.subsets:
            # Make sure unions are created again
            self.version += 1

            if not isinstance(event, AssociationUpdated):
                return

            values = self._union(event.element, exclude=event.property)

            if self.upper == 1:
                assert isinstance(event, AssociationSet)
                old_value, new_value = event.old_value, event.new_value
                # This is a [0..1] event
                if self.single:
                    # Only one subset element, so pass the values on
                    self.handle(DerivedSet(event.element, self, old_value, new_value))
                else:
                    new_values = set(values)
                    if new_value:
                        new_values.add(new_value)
                    if len(new_values) > 1:
                        # In an in-between state. Do not emit notifications
                        return
                    if values:
                        new_value = next(iter(values))
                    self.handle(DerivedSet(event.element, self, old_value, new_value))
            else:
                if isinstance(event, AssociationSet):
                    old_value, new_value = event.old_value, event.new_value
                    if old_value and old_value not in values:
                        self.handle(DerivedDeleted(event.element, self, old_value))
                    if new_value and new_value not in values:
                        self.handle(DerivedAdded(event.element, self, new_value))

                elif isinstance(event, AssociationAdded):
                    new_value = event.new_value
                    if new_value not in values:
                        self.handle(DerivedAdded(event.element, self, new_value))

                elif isinstance(event, AssociationDeleted):
                    old_value = event.old_value
                    if old_value not in values:
                        self.handle(DerivedDeleted(event.element, self, old_value))

                elif isinstance(event, AssociationUpdated):
                    self.handle(DerivedUpdated(event.element, self))
                else:
                    log.error(
                        "Don't know how to handle event "
                        + str(event)
                        + " for derived union"
                    )


class redefine(umlproperty[T]):
    """
    Redefined association

      Element.redefine = redefine(Element, 'redefine', Class, Element.assoc)

    If the redefine eclipses the original property (it has the same name)
    it ensures that the original values are saved and restored.
    """

    def __init__(
        self,
        decl_class: Type[E],
        name: str,
        type: Type[T],
        upper: Upper,
        original: relation,
    ):
        super().__init__(name)
        assert isinstance(
            original, (association, derived)
        ), f"expected association or derived, got {original}"
        assert (
            upper == original.upper
        ), f"Multiplicity of {decl_class}.{name} and {original} differ: {upper} != {original.upper}"
        self.decl_class = decl_class
        self.name = name
        self._name = "_" + name
        self.type = type
        self.original = original
        self.upper = original.upper
        self.lower = original.lower

        original._dependent_properties.add(self)

    @property
    def opposite(self) -> Optional[str]:
        return (
            self.original.opposite if isinstance(self.original, association) else None
        )

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

    def __str__(self) -> str:
        return f"<redefine {self.name}[{self.lower}..{self.upper}]: {self.type.__name__} = {str(self.original)}>"

    def __get__(self, obj, class_=None):
        # No longer needed
        if not obj:
            return self
        return self.original.__get__(obj, class_)

    def __set__(self, obj, value: T) -> None:
        # No longer needed
        if not isinstance(value, self.type):
            raise AttributeError(f"Value should be of type {self.type.__name__}")
        self.original.__set__(obj, value)

    def __delete__(self, obj, value=None):
        # No longer needed
        self.original.__delete__(obj, value)

    def _get(self, obj):
        return self.original._get(obj)

    def _set(self, obj, value, from_opposite=False):
        assert isinstance(self.original, association)
        return self.original._set(obj, value, from_opposite)

    def _del(self, obj, value, from_opposite=False):
        assert isinstance(self.original, association)
        return self.original._del(obj, value, from_opposite)

    def propagate(self, event):
        if event.property is self.original and isinstance(
            event.element, self.decl_class
        ):
            # mimic the events for Set/Add/Delete
            if isinstance(event, AssociationSet):
                self.handle(
                    RedefinedSet(event.element, self, event.old_value, event.new_value)
                )
            elif isinstance(event, AssociationAdded):
                self.handle(RedefinedAdded(event.element, self, event.new_value))
            elif isinstance(event, AssociationDeleted):
                self.handle(RedefinedDeleted(event.element, self, event.old_value))
            else:
                log.error(
                    "Don't know how to handle event "
                    + str(event)
                    + " for redefined association"
                )
