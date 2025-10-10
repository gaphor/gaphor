"""Properties used to create the Gaphor data models.

The logic for creating and destroying connections between elements is
implemented in Python property classes. These classes are simply instantiated
like this:
    class Class(Element): pass
    class Comment(Element): pass
    Class.comment = association('comment', Comment,
                                     0, '*', 'annotatedElement')
    Comment.annotatedElement = association('annotatedElement', Element,
                                           0, '*', 'comment')

Same for attributes and enumerations.

Each property type (association, attribute and enumeration) has three specific
methods:
    get():           return the value
    set(value):      set the value or add it to a list
    delete(value=None): delete the value. 'value' is used to tell which value
                      is to be removed (in case of associations with
                      multiplicity > 1).
    load(value):      load 'value' as the current value for this property
    save(save_func):  send the value of the property to save_func(name, value)
"""

from __future__ import annotations

import enum
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import (
    Any,
    Literal,
    Protocol,
    TypeVar,
    overload,
)

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.event import (
    AssociationAdded,
    AssociationDeleted,
    AssociationSet,
    AssociationUpdated,
    AttributeUpdated,
    DerivedAdded,
    DerivedDeleted,
    DerivedSet,
    DerivedUpdated,
    RedefinedAdded,
    RedefinedDeleted,
    RedefinedSet,
    RedefinedUpdated,
)

__all__ = ["attribute", "enumeration", "association", "derivedunion", "redefine"]


log = logging.getLogger(__name__)


UnlimitedNatural = int | Literal["*"]


E = TypeVar("E")


class relation_one(Protocol[E]):
    def get(self, obj) -> E | None: ...

    def set(self, obj, value: E | None) -> None: ...

    def delete(self, obj, value: E | None) -> None: ...

    @overload
    def __get__(self, obj: None, class_=None) -> relation_one[E]: ...

    @overload
    def __get__(self, obj, class_=None) -> E: ...

    def __set__(self, obj, value: E | None) -> None: ...

    def __delete__(self, obj) -> None: ...


class relation_many(Protocol[E]):
    def get(self, obj) -> collection[E]: ...

    def set(self, obj, value: E) -> None: ...

    def delete(self, obj, value: E) -> None: ...

    @overload
    def __get__(self, obj: None, class_=None) -> relation_many[E]: ...

    @overload
    def __get__(self, obj, class_=None) -> collection[E]: ...

    def __set__(self, obj, value: E) -> None: ...

    def __delete__(self, obj) -> None: ...


relation = relation_one | relation_many


T = TypeVar("T")

Lower = Literal[0] | Literal[1] | Literal[2]
Upper = Literal[1] | Literal[2] | Literal["*"]


class umlproperty:
    """Superclass for an attribute, enumeration, and association.

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
        self.dependent_properties: set[subsettable_umlproperty | redefine] = set()
        self.name = name
        self._name = f"_{name}"

    def __get__(self, obj, class_=None):
        return self.get(obj) if obj else self

    def __set__(self, obj, value) -> None:
        self.set(obj, value)

    def __delete__(self, obj) -> None:
        self.delete(obj, None)

    def __repr__(self):
        return str(self)

    def save(self, obj, save_func: Callable[[str, object], None]):
        if hasattr(obj, self._name):
            save_func(self.name, self.get(obj))

    def load(self, obj, value):
        self.set(obj, value)

    def postload(self, obj):
        pass

    def unlink(self, obj):
        """This is called from the Element to denote the element is
        unlinking."""

    def get(self, obj) -> T | None | collection[T]:
        raise NotImplementedError()

    def set(self, obj, value: T | None) -> None:
        raise NotImplementedError()

    def delete(self, obj, value: T | None) -> None:
        raise NotImplementedError()

    def handle(self, event):
        event.element.handle(event)
        for d in self.dependent_properties:
            d.propagate(event)


class subsettable_umlproperty(umlproperty):
    """Base class for properties that can be subsetted"""

    subsets: set[umlproperty]

    def __init__(self, name: str):
        super().__init__(name)
        self.subsets = set()

    def add(self, subset):
        if self.upper == 1 and subset.upper == "*":
            log.warning(
                "Modeling error: Cannot add a multiplicity * subset "
                + subset.name
                + " to a multiplicity 1 superset "
                + self.name
            )
        self.subsets.add(subset)
        assert isinstance(subset, association | derived | redefine), (
            f"have element {subset}, expected association, derived or redefine"
        )
        subset.dependent_properties.add(self)

    def propagate(self, event): ...


class attribute[T](umlproperty):
    """Attribute.

    Element.attr = attribute('attr', str, '')
    """

    def __init__(
        self,
        name: str,
        type: type[str | int | bool],
        default: str | int | None = None,
    ):
        super().__init__(name)
        self.type = type
        self.default: str | int | None = default

    def load(self, obj, value: str | None):
        """Load the attribute value."""
        self.set(obj, value)

    def unlink(self, obj):
        self.set(obj, self.default)

    def __str__(self):
        return f"<attribute {self.name}: {self.type} = {self.default}>"

    def get(self, obj):
        return getattr(obj, self._name, self.default)

    def set(self, obj, value):
        if (
            value is not None
            and self.type is not UnlimitedNatural
            and not isinstance(value, str | self.type)
        ):
            raise TypeError(f"Value should be of type {self.type}, not {type(value)}")

        elif value is not None and self.type is UnlimitedNatural:
            if value != "*":
                value = int(value)
                if value < 0:
                    raise ValueError(
                        "Value for UnlimitedNatural should be int >= 0, or '*'"
                    )

        elif self.type is int and isinstance(value, str | bool):
            value = (
                0
                if value == "False"
                else 1
                if value == "True"
                else "*"
                if value == "*"
                else int(value)
            )

        if value == self.get(obj):
            return

        old = self.get(obj)
        if value == self.default and hasattr(obj, self._name):
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.handle(AttributeUpdated(obj, self, old, value))

    def delete(self, obj, value=None):
        old = self.get(obj)
        try:
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.handle(AttributeUpdated(obj, self, old, self.default))


class enumeration(umlproperty):
    """Enumeration.

      Element.enum = enumeration('enum', EnumKind, 'one')

    An enumeration is a special kind of attribute that can only hold a
    predefined set of values. Multiplicity is always `[0..1]`.
    """

    def __init__(self, name: str, type: type[enum.StrEnum], default: enum.StrEnum):
        super().__init__(name)
        self.type = type
        self.default = default

    def __str__(self):
        return f"<enumeration {self.name}: {self.type.__name__} = {self.default}>"

    def get(self, obj):
        return getattr(obj, self._name, self.default)

    def load(self, obj, value: str | None):
        self.set(obj, self.default if value is None else value)

    def unlink(self, obj):
        self.set(obj, self.default)

    def set(self, obj, value):
        if value not in self.type:
            raise TypeError(f"Value should be one of {list(self.type)}")
        old = self.get(obj)
        if value == old:
            return

        if value == self.default:
            delattr(obj, self._name)
        else:
            setattr(obj, self._name, value)
        self.handle(AttributeUpdated(obj, self, old, value))

    def delete(self, obj, value=None):
        old = self.get(obj)
        try:
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            self.handle(AttributeUpdated(obj, self, old, self.default))


class association(subsettable_umlproperty):
    """Association, both uni- and bi-directional.

    Element.assoc = association('assoc', Element, opposite='other')

    We connect a listener to the value added to the association. This will
    cause the association to be ended if we unlink the element on the other end
    of the association.

    If the association is a composite relationship, the association will
    unlink all elements attached to if it is unlinked.

    Associations may be subsets of other associations or sets. The subset must have a
    multiplicity less than or equal to the superset.

    The logic of maintaining the set contets is complex. While this logic is constrained by set
    theory, there are cases that arise in which set theory alone would allow multiple outcomes.
    Making the outcomes deterministic requires making some policy choices. In the cases below,
    those marked with ***POLICY*** are not solely determined by the logic of set theory.

    The handling of the subset-superset relation depends upon the nature of the superset.
        If the superset is a derived union, the removal of an element from the subset should also remove
            it from the superset unless the element is present in the superset because of a different subset.
        If the superset is an ordinary collection, the behavior depends upon the multiplicity of the set.
            If the superset has an allowed multiplicity > 1, the removal of an element from the subset should not
                cause the element to be removed from the superset.
            If the superset has an allowed multiplicity of 1, the removal of an element from the subset should
                cause the element to be removed from the superset.
        if the superset is an ordinary collection and an element is removed from the superset, it must
            also be removed from the subset.

    Subset changes, both sets have a multiplicity of 1:
        Both sets {}: subset {a1} => superset {a1}
        Superset {a1}, subset {}: subset {a2} => superset {a2} ***POLICY***
        Derived Union: Superset {a1}, subset {a1}: subset {} => superset {} ***POLICY***
        Ordinary Collection: Superset {a1}, subset {a1}: subset {} => superset {a1} ***POLICY***
        Superset {a1}, subset {a1}: subset {a2} => superset {a2} ***POLICY***

    Superset changes, both sets have a multiplicity of 1:
        Both sets {}: superset {a1} => subset {}
        Subset {a1}, superset {a1}: superset {}, => subset {}
        Superset {a1}, subset {a1}: superset {a2} => subset {}

    Subset changes, superset has multiplicity *, subset has multiplicity 1 or *:
        Both sets {}: subset {a1} => superset {a1}
        Superset {a1}, subset {}, subset {a2} => superset {a1, a2}
        Derived Union: Superset {a1}, subset {a1}: subset {} => superset {} ***POLICY***
        Ordinary Collection: Superset {a1}, subset {a1}: subset {} => superset {a1} ***POLICY***
        Derived Union: Superset {a1}, subset {a1}: subset {a2}, => superset {a2} ***POLICY***
            assuming that a1 is not in another subset of the derived union
        Ordinary Collection: Superset {a1}, subset {a1}: subset {a2}, => superset {a1, a2} ***POLICY***

    Superset changes, superset has multiplicity *, subset has multiplicity 1 or *:
        Both sets {}: superset {a1} => subset {}
        Superset {a1}, subset {a1}: superset {} => subset {}
        Superset {a1}, subset {a1}, superset {a2} => subset {}
    """

    def __init__(
        self,
        name: str,
        type: type,
        lower: Lower = 0,
        upper: Upper = "*",
        composite: bool = False,
        opposite: str | None = None,
    ):
        super().__init__(name)
        self.type = type
        self.lower = lower
        self.upper = upper
        self.composite = composite
        self.opposite = opposite
        self.stub: associationstub | None = None

    def save(self, obj, save_func: Callable[[str, object], None]):
        if hasattr(obj, self._name):
            if v := self.get(obj):
                save_func(self.name, v)

    def load(self, obj, value):
        if self.opposite:
            # Loading should not steal references from other elements
            opposite = getattr(type(value), self.opposite)
            if opposite.upper == 1 and (opval := opposite.get(value)):
                if opval is not obj:
                    log.debug(f"Cannot steal reference from {value}")
                return

        self.set(obj, value)

    def __str__(self):
        if self.lower == self.upper:
            s = f"<association {self.name}: {self.type.__name__}[{self.lower}]"
        else:
            s = f"<association {self.name}: {self.type.__name__}[{self.lower}..{self.upper}]"
        if self.opposite:
            s += f" {self.composite and '<>' or ''}-> {self.opposite}"
        return f"{s}>"

    def get(self, obj):
        return self._get_one(obj) if self.upper == 1 else self._get_many(obj)

    def _get_one(self, obj) -> T | None:
        return getattr(obj, self._name, None)

    def _get_many(self, obj) -> collection[T]:
        v: collection[T] | None = getattr(obj, self._name, None)
        if v is None:
            # Create the empty collection here since it may
            # be used to add.
            v = collection(self, obj, self.type)
            setattr(obj, self._name, v)
        return v

    def set(
        self, obj, value: T | None, index: int | None = None, from_opposite=False
    ) -> None:
        """Set a new value for our attribute. If this is a collection, append
        to the existing collection.

        This method is called from the opposite association property.
        """
        if obj is value:
            raise TypeError(f"Cannot set {obj}.{self.name} to itself")

        if self.upper == 1:
            self._set_one(obj, value, from_opposite)
        else:
            self._set_many(obj, value, index, from_opposite)

    def _set_one(self, obj, value, from_opposite=False) -> None:
        if not (isinstance(value, self.type) or (value is None)):
            raise TypeError(
                f"Value should be of type {self.type.__modeling_language__}:{self.type.__name__}, got a {type(value)} instead"  # type: ignore[attr-defined]
            )

        old = self._get_one(obj)

        # do nothing if we are assigned our current value:
        # Still do your thing, since undo handlers expect that.
        if value is old:
            return

        if old:
            self._del_one(obj, old, do_notify=False)

        if value is not None:
            setattr(obj, self._name, value)
            try:
                self._set_opposite(obj, value, from_opposite)
            except Exception:
                setattr(obj, self._name, old)
                raise

        self.handle(AssociationSet(obj, self, old, value))

    def _set_many(
        self, obj, value, index, from_opposite=False, from_load=False
    ) -> None:
        if not value:
            return None
        if not isinstance(value, self.type):
            raise TypeError(
                f"Value should be of type {self.type.__modeling_language__}:{self.type.__name__}"  # type: ignore[attr-defined]
            )

        # Set the actual value
        c: collection = self._get_many(obj)
        if value in c:
            if from_load:
                c.items.remove(value)
                if index is None:
                    c.items.append(value)
                else:
                    c.items.insert(index, value)
            return

        if index is None:
            c.items.append(value)
        else:
            c.items.insert(index, value)

        try:
            self._set_opposite(obj, value, from_opposite)
        except Exception:
            if value in c.items:
                c.items.remove(value)
            raise

        self.handle(AssociationAdded(obj, self, value))

    def _set_opposite(self, obj, value: T | None, from_opposite=False) -> None:
        if not from_opposite and self.opposite:
            opposite = getattr(type(value), self.opposite)
            if not opposite.opposite:
                opposite.stub = self
            if not isinstance(opposite, derived):
                opposite.set(value, obj, from_opposite=True)
            else:
                log.warning(
                    f"Cannot set opposite of association {self.name} since the opposite {opposite.name} is derived"
                )
        elif not self.opposite:
            if not self.stub:
                self.stub = associationstub(self)
                # Do not let property start with underscore, or it will not be found
                # as an umlproperty.
                setattr(self.type, f"GAPHOR__associationstub__{id(self):x}", self.stub)
            self.stub.set(value, obj)

    def delete(self, obj, value, from_opposite=False, do_notify=True):
        """Delete is used for element deletion and for removal of elements from
        a list."""
        if self.upper == 1:
            self._del_one(obj, self._get_one(obj), from_opposite, do_notify)
        else:
            self._del_many(obj, value, from_opposite, do_notify)

    def _del_one(self, obj, value, from_opposite=False, do_notify=True):
        if value is None:
            return

        self._del_opposite(obj, value, from_opposite)

        try:
            delattr(obj, self._name)
        except AttributeError:
            pass
        else:
            if do_notify:
                self.handle(AssociationSet(obj, self, value, None))
            for subset in self.subsets:
                if value == subset.get(obj):
                    subset.delete(obj, value)

    def _del_many(self, obj, value, from_opposite=False, do_notify=True):
        if not value:
            raise Exception("Can not delete collections")

        self._del_opposite(obj, value, from_opposite)

        c: collection
        if c := self._get_many(obj):
            items: list = c.items
            try:
                index = items.index(value)
                items.remove(value)
            except ValueError:
                pass
            else:
                if do_notify:
                    self.handle(AssociationDeleted(obj, self, value, index))
                for subset in self.subsets:
                    col: collection[umlproperty] | umlproperty | None = subset.get(obj)
                    if isinstance(col, collection) and value in col:
                        subset.delete(obj, value)

            # Remove items collection if empty
            if not items:
                delattr(obj, self._name)

    def _del_opposite(self, obj, value, from_opposite):
        if not from_opposite and self.opposite:
            getattr(type(value), self.opposite).delete(value, obj, from_opposite=True)
        elif not self.opposite:
            if self.stub:
                self.stub.delete(value, obj, from_opposite=True)

    def unlink(self, obj):
        if values := self.get(obj):
            if self.upper == 1:
                values = [values]

            composite = self.composite
            for value in list(values):
                self.delete(obj, value)
                if composite:
                    value.unlink()

    def propagate(self, event):
        if event.property not in self.subsets:
            return
        if not isinstance(event, AssociationUpdated):
            return

        current_value = self.get(event.element)

        upper_gt_1 = self.upper == "*" or int(self.upper) > 1
        if isinstance(event, AssociationSet):
            if event.new_value != current_value:
                # new_value is coming from a subset. If the value is None and self is not derived
                # and has upper > 1 then we make no change to this association.
                not_derived = not isinstance(self, derived)
                null_value = event.new_value is None
                if not (not_derived and null_value and upper_gt_1):
                    self.set(event.element, event.new_value)
        elif isinstance(event, AssociationDeleted):
            value = self.get(event.element)
            if isinstance(value, collection):
                if event.old_value in self.get(event.element):
                    # new_value is coming from a subset. If self is not derived and this is a collection
                    # we make no change to this association.
                    if isinstance(self, derived) or not upper_gt_1:
                        self.delete(event.element, event.old_value)
            elif event.old_value is value:
                # new_value is coming from a subset. If self is not derived and this is a collection
                # we make no change to this association.
                if isinstance(self, derived) or not upper_gt_1:
                    self.delete(event.element, event.old_value)
        elif isinstance(event, AssociationAdded):
            self.set(event.element, event.new_value)


class AssociationStubError(Exception):
    pass


class associationstub(umlproperty):
    """An association stub is an internal thingy that ensures all associations
    are always bidirectional.

    This helps the application when one end of the association is
    unlinked. On unlink() of an element all `umlproperty`'s are iterated
    and called by their unlink() method.
    """

    def __init__(self, association: association):
        super().__init__(f"stub_{id(self):x}")
        self.association = association

    def __get__(self, obj, class_=None):
        if obj:
            raise AssociationStubError("getting values not allowed")
        return self

    def __set__(self, obj, value):
        raise AssociationStubError("setting values not allowed")

    def __delete__(self, obj):
        raise AssociationStubError("deleting values not allowed")

    def save(self, obj, save_func):
        pass

    def load(self, obj, value):
        pass

    def unlink(self, obj):
        values = getattr(obj, self._name, [])
        for value in set(values):
            self.association.delete(value, obj)

    def set(self, obj, value):
        try:
            getattr(obj, self._name).add(value)
        except AttributeError:
            setattr(obj, self._name, {value})

    def delete(self, obj, value, from_opposite=False):
        try:
            c = getattr(obj, self._name)
        except AttributeError:
            pass
        else:
            c.discard(value)


@dataclass
class unioncache:
    """Small cache helper object for derivedunions."""

    owner: object
    data: object
    version: int


class derived[T](subsettable_umlproperty):
    """Base class for derived properties, both derived unions and custom
    properties.

    Note that, although this derived property sends DerivedAdded,
    -Delete- and Set events, this gives just an assumption that something
    may have changed. If something actually changed depends on the filter
    applied to the derived property.

    NB. filter returns a *list* of filtered items, even when upper bound is 1.
    """

    opposite = None

    def __init__(  # type: ignore[explicit-any]
        self,
        name: str,
        type: type[T],
        lower: Lower,
        upper: Upper,
        filter: Callable[[Any], list[T | None]],
        *subsets: relation,
    ) -> None:
        super().__init__(name)
        self.version = 1
        self.type = type
        self.lower = lower
        self.upper = upper
        self.filter = filter

        for s in subsets:
            self.add(s)

    def load(self, obj, value):
        raise ValueError(
            f"Derivedunion: Properties should not be loaded in a derived union {self.name}: {value}"
        )

    def postload(self, obj):
        self.version += 1

    def save(self, obj, save_func):
        pass

    def __str__(self):
        return f"<derived {self.name}: {self.type} {str(list(map(str, self.subsets)))[1:-1]}>"

    def _update(self, obj):
        """Update the list of items.

        Returns an unioncache instance.
        """
        u = self.filter(obj)
        if self.upper == 1:
            uc = unioncache(self, u[0] if u else None, self.version)
        else:
            c = collection(self, obj, self.type)
            c.items.extend(u)  # type: ignore[arg-type]
            uc = unioncache(self, c, self.version)
        setattr(obj, self._name, uc)
        return uc

    def get(self, obj):
        if self.subsets:
            try:
                uc = getattr(obj, self._name)
                if uc.version != self.version:
                    uc = self._update(obj)
                assert self is uc.owner
            except AttributeError:
                uc = self._update(obj)
        else:
            uc = self._update(obj)
        return uc.data

    def set(self, obj, value):
        raise AttributeError(f"Cannot set values on union {self.name}: {self.type}")

    def delete(self, obj, value=None):
        raise AttributeError(f"Can not delete values on union {self.name}: {self.type}")

    def propagate(self, event):
        """Re-emit state change for the derived properties as Derived*Event's.

        If multiplicity is [0..1]:   send DerivedSet if len(union) < 2
        if multiplicity is [*]:   send DerivedAdded and DerivedDeleted
        if value not in derived union and
        """
        if event.property not in self.subsets:
            return
        if not isinstance(event, AssociationUpdated):
            return

        # mimic the events for Set/Add/Delete
        if self.upper == 1:
            old_value = hasattr(event.element, self._name) and self.get(event.element)
            # Make sure unions are created again
            self.version += 1
            new_value = self.get(event.element)
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


def object_has_property(obj, prop):
    found = getattr(type(obj), prop.name, None)
    while isinstance(found, redefine):
        found = found.original
    return prop is found


class derivedunion(derived[T]):
    """Derived union.

      Element.union = derivedunion('union', subset1, subset2..subsetn)

    The subsets are the properties that participate in the union (Element.name).
    """

    def __init__(
        self,
        name: str,
        type: type[T],
        lower: Lower = 0,
        upper: Upper = "*",
        *subsets: relation,
    ):
        super().__init__(name, type, lower, upper, self._union, *subsets)

    def _union(self, obj, exclude=None):
        """Returns a union of all values as a set."""
        u: set[T] = set()
        for s in self.subsets:
            if s is exclude or not object_has_property(obj, s):
                continue

            tmp: Iterable[T] | T | None = s.get(obj)
            if isinstance(tmp, Iterable):
                u.update(tmp)
            elif tmp:
                # [0..1] property
                u.add(tmp)
        return list(u)

    def propagate(self, event):
        """Re-emit state change for the derived union (as Derived*Event's).

        If multiplicity is [0..1]:   send DerivedSet if len(union) < 2
        if multiplicity is [*]:   send DerivedAdded and DerivedDeleted
        if value not in derived union and
        """
        if event.property not in self.subsets:
            return
        # Make sure unions are created again
        self.version += 1

        if not isinstance(event, AssociationUpdated):
            return

        values = set(self._union(event.element, exclude=event.property))

        if self.upper == 1:
            assert isinstance(event, AssociationSet)
            old_value, new_value = event.old_value, event.new_value
            # This is a [0..1] event
            if len(self.subsets) > 1:
                new_values = set(values)
                if new_value:
                    new_values.add(new_value)
                if len(new_values) > 1:
                    # In an in-between state. Do not emit notifications
                    return
                if values:
                    new_value = next(iter(values))
            # Only one subset element, so pass the values on
            self.handle(DerivedSet(event.element, self, old_value, new_value))
        elif isinstance(event, AssociationSet):
            old_value, new_value = event.old_value, event.new_value
            if old_value and old_value not in values:
                pass
                # Change so that deletions from subsets no longer delete from superset
                # self.handle(DerivedDeleted(event.element, self, old_value))
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
            log.error(f"Don't know how to handle event {event} for derived union")


class redefine(umlproperty):
    """Redefined association.

      Element.redefine = redefine(Element, 'redefine', Class, Element.assoc)

    If the redefine eclipses the original property (it has the same name)
    it ensures that the original values are saved and restored.
    """

    def __init__(
        self,
        decl_class: type[E],
        name: str,
        type: type[T],
        original: relation,
        opposite: str | None = None,
    ):
        super().__init__(name)
        assert isinstance(original, association | derived), (
            f"expected association or derived, got {original}"
        )
        self.decl_class = decl_class
        self.type = type
        self.original: association | derived = original
        self.upper = original.upper
        self.lower = original.lower
        self._opposite = opposite

        original.dependent_properties.add(self)

    @property
    def opposite(self) -> str | None:
        if self._opposite:
            return self._opposite
        elif isinstance(self.original, association):
            return self.original.opposite
        return None

    @property
    def composite(self) -> bool:
        return (
            self.original.composite if isinstance(self.original, association) else False
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
        return f"<redefine {self.name}[{self.lower}..{self.upper}]: {self.type.__name__} = {self.original}>"

    def get(self, obj):
        return self.original.get(obj)

    def set(self, obj, value, from_opposite=False):
        if not (isinstance(value, self.type) or (self.upper == 1 and value is None)):
            raise TypeError(
                f"Value should be of type {self.type.__modeling_language__}:{self.type.__name__}, got a {type(value)} instead"  # type: ignore[attr-defined]
            )
        assert isinstance(self.original, association)
        return self.original.set(obj, value, from_opposite=from_opposite)

    def delete(self, obj, value, from_opposite=False, do_notify=True):
        assert isinstance(self.original, association)
        return self.original.delete(obj, value, from_opposite, do_notify)

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
                self.handle(
                    RedefinedDeleted(event.element, self, event.old_value, event.index)
                )
            elif isinstance(event, AssociationUpdated):
                self.handle(RedefinedUpdated(event.element, self))
            else:
                log.error(
                    "Don't know how to handle event "
                    + str(event)
                    + " for redefined association"
                )
