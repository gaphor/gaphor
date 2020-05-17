"""
1:n and n:m relations in the data model are saved using a collection.
"""

import inspect
from typing import Generic, List, Type, TypeVar, Union, overload

from gaphor.core.modeling.event import AssociationUpdated
from gaphor.core.modeling.listmixins import querymixin, recursemixin, recurseproxy

T = TypeVar("T")


class collectionlist(recursemixin, querymixin, List[T]):  # type: ignore[misc]
    """
    >>> c = collectionlist()
    >>> c.append('a')
    >>> c.append('b')
    >>> c.append('c')
    >>> c
    ['a', 'b', 'c']

    It should work with the datamodel too:

    >>> from gaphor.UML import *
    >>> c = Class()
    >>> c.ownedOperation = Operation()
    >>> c.ownedOperation   # doctest: +ELLIPSIS
    [<gaphor.UML.uml.Operation element ...>]
    >>> c.ownedOperation[0]   # doctest: +ELLIPSIS
    <gaphor.UML.uml.Operation element ...>
    >>> c.ownedOperation = Operation()
    >>> c.ownedOperation[0].formalParameter = Parameter()
    >>> c.ownedOperation[0].formalParameter = Parameter()
    >>> c.ownedOperation[0].formalParameter[0].name = 'foo'
    >>> c.ownedOperation[0].formalParameter[0].name
    'foo'
    >>> c.ownedOperation[0].formalParameter[1].name = 'bar'
    >>> list(c.ownedOperation[0].formalParameter[:].name)
    ['foo', 'bar']
    >>> c.ownedOperation[:].formalParameter.name   # doctest: +ELLIPSIS
    <gaphor.core.modeling.listmixins.recurseproxy object at 0x...>
    >>> list(c.ownedOperation[:].formalParameter.name)
    ['foo', 'bar']
    >>> c.ownedOperation[0].formalParameter['it.name=="foo"', 0].name
    'foo'
    >>> c.ownedOperation[:].formalParameter['it.name=="foo"', 0].name
    'foo'
    """


class collection(Generic[T]):
    """
    Collection (set-like) for model elements' 1:n and n:m relationships.
    """

    def __init__(self, property, object, type: Type[T]):
        self.property = property
        self.object = object
        self.type = type
        self.items: collectionlist[T] = collectionlist()

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

    def __getitem__(self, key: Union[int, slice]):
        return self.items.__getitem__(key)

    def __contains__(self, obj) -> bool:
        return self.items.__contains__(obj)

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return str(self.items)

    __repr__ = __str__

    def __bool__(self):
        return self.items != []

    def append(self, value: T) -> None:
        if isinstance(value, self.type):
            self.property._set(self.object, value)
        else:
            raise TypeError(f"Object is not of type {self.type.__name__}")

    def remove(self, value: T) -> None:
        if value in self.items:
            self.property.__delete__(self.object, value)

    def index(self, key: T) -> int:
        """
        Given an object, return the position of that object in the
        collection.
        """
        return self.items.index(key)

    # OCL members (from SMW by Ivan Porres, http://www.abo.fi/~iporres/smw)

    def size(self):
        return len(self.items)

    def includes(self, o):
        return o in self.items

    def excludes(self, o):
        return not self.includes(o)

    def count(self, o):
        c = 0
        for x in self.items:
            if x == o:
                c = c + 1
        return c

    def includesAll(self, c):
        for o in c:
            if o not in self.items:
                return 0
        return 1

    def excludesAll(self, c):
        for o in c:
            if o in self.items:
                return 0
        return 1

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
        """
        Swap two elements. Return true if swap was successful.
        """
        try:
            i1 = self.items.index(item1)
            i2 = self.items.index(item2)
            self.items[i1], self.items[i2] = self.items[i2], self.items[i1]

            self.object.handle(AssociationUpdated(self.object, self.property))
            return True
        except (IndexError, ValueError):
            return False

    def order(self, key):
        self.items.sort(key=key)
