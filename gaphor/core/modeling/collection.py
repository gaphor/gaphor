"""1:n and n:m relations in the data model are saved using a collection."""

from __future__ import annotations

import contextlib
from typing import Generic, Iterator, Sequence, Type, TypeVar, overload

from gaphor.core.modeling.event import AssociationUpdated

T = TypeVar("T")


class collection(Generic[T]):
    """Collection (set-like) for model elements' 1:n and n:m relationships."""

    def __init__(self, property, object, type: Type[T]):
        self.property = property
        self.object = object
        self.type = type
        self.items: list[T] = []

    def __len__(self) -> int:
        return len(self.items)

    def __setitem__(self, key, value) -> None:
        raise RuntimeError("items should not be overwritten.")

    def __delitem__(self, key: T) -> None:
        self.remove(key)

    @overload
    def __getitem__(self, key: int) -> T:
        ...

    @overload  # Literal[slice(None, None, None)]
    def __getitem__(self, key: slice) -> recurseproxy[T]:
        ...

    def __getitem__(self, key):
        if key == _recurseproxy_trigger:
            return recurseproxy(self.items)
        return self.items.__getitem__(key)

    def __contains__(self, obj) -> bool:
        return self.items.__contains__(obj)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __str__(self):
        return f"collection({self.items})"

    __repr__ = __str__

    def __bool__(self):
        return self.items != []

    def __eq__(self, other):
        return self.items == other or (
            isinstance(other, collection) and self.items == other.items
        )

    def __hash__(self):
        return hash(str(self))

    def index(self, key: T) -> int:
        """Given an object, return the position of that object in the
        collection."""
        return self.items.index(key)

    def append(self, value: T) -> None:
        if isinstance(value, self.type):
            self.property.set(self.object, value)
        else:
            raise TypeError(f"Object is not of type {self.type.__name__}")

    def remove(self, value: T) -> None:
        if value in self.items:
            self.property.delete(self.object, value)

    # OCL members (from SMW by Ivan Porres, http://www.abo.fi/~iporres/smw)

    def size(self):
        return len(self.items)

    def includes(self, o):
        return o in self.items

    def excludes(self, o):
        return not self.includes(o)

    def count(self, o):
        return self.items.count(o)

    def includesAll(self, c):
        return all(o in self.items for o in c)

    def excludesAll(self, c):
        return all(o not in self.items for o in c)

    def select(self, f):
        return [v for v in self.items if f(v)]

    def reject(self, f):
        return [v for v in self.items if not f(v)]

    def collect(self, f):
        return [f(v) for v in self.items]

    def isEmpty(self):
        return len(self.items) == 0

    def nonEmpty(self):
        return not self.isEmpty()

    def swap(self, item1, item2):
        """Swap two elements.

        Return true if swap was successful.
        """
        try:
            i1 = self.items.index(item1)
            i2 = self.items.index(item2)
            self.items[i1], self.items[i2] = self.items[i2], self.items[i1]
        except (IndexError, ValueError):
            return False
        else:
            self.object.handle(AssociationUpdated(self.object, self.property))
            return True

    def order(self, key):
        self.items.sort(key=key)
        self.object.handle(AssociationUpdated(self.object, self.property))


_recurseproxy_trigger = slice(None, None, None)


class recurseproxy(Generic[T]):
    """Proxy object (helper) for the recusemixin.

    The proxy has limited capabilities compared to a real list (or set):
    it can be iterated and a getitem can be performed. On the other
    side, the type of the original sequence is maintained, so getitem
    operations act as if they're executed on the original list.
    """

    def __init__(self, sequence: Sequence[T]):
        self.__sequence = sequence

    def __getitem__(self, key: int | slice) -> T:
        return self.__sequence.__getitem__(key)  # type: ignore[return-value]

    def __iter__(self):
        """Iterate over the items.

        If there is some level of nesting, the parent items are iterated
        as well.
        """
        return iter(self.__sequence)

    def __getattr__(self, key: str) -> recurseproxy[T]:
        """Create a new proxy for the attribute."""

        def mygetattr():
            sentinel = object()
            for e in self.__sequence:
                obj = getattr(e, key, sentinel)
                if obj is sentinel:
                    pass
                elif issafeiterable(obj):
                    yield from obj  # type: ignore[misc]
                else:
                    yield obj

        # Create a copy of the proxy type, including a copy of the sequence type
        return type(self)(type(self.__sequence)(mygetattr()))  # type: ignore[call-arg]


def issafeiterable(obj):
    """Checks if the object is iterable, but not a string.

    >>> issafeiterable([])
    True
    >>> issafeiterable(set())
    True
    >>> issafeiterable({})
    True
    >>> issafeiterable(1)
    False
    >>> issafeiterable("text")
    False
    """
    with contextlib.suppress(TypeError):
        return iter(obj) and not isinstance(obj, str)
    return False
