#!/usr/bin/python

# This is Gaphor, a Python+GTK modeling tool

# Copyright 2001-2004, 2007, 2009 Arjan Molenaar, 2010 Artur Wroblewski, 2017 Dan Yeaw

# Gaphor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Gaphor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.

"""
1:n and n:m relations in the data model are saved using a collection.
"""

from __future__ import absolute_import

import inspect

from gaphor.UML.event import AssociationChangeEvent
from gaphor.misc.listmixins import querymixin, recursemixin, getslicefix


class collectionlist(recursemixin, querymixin, getslicefix, list):
    """
    >>> c = collectionlist()
    >>> c.append('a')
    >>> c.append('b')
    >>> c.append('c')
    >>> c
    ['a', 'b', 'c']

    It should work with the datamodel too:

    >>> from gaphor.UML import uml2
    >>> c = uml2.Class()
    >>> c.ownedOperation = uml2.Operation()
    >>> c.ownedOperation   # doctest: +ELLIPSIS
    [<gaphor.UML.uml2.Operation object at 0x...>]
    >>> c.ownedOperation[0]   # doctest: +ELLIPSIS
    <gaphor.UML.uml2.Operation object at 0x...>
    >>> c.ownedOperation = uml2.Operation()
    >>> c.ownedOperation[0].formalParameter = uml2.Parameter()
    >>> c.ownedOperation[0].formalParameter = uml2.Parameter()
    >>> c.ownedOperation[0].formalParameter[0].name = 'foo'
    >>> c.ownedOperation[0].formalParameter[0].name
    'foo'
    >>> c.ownedOperation[0].formalParameter[1].name = 'bar'
    >>> list(c.ownedOperation[0].formalParameter[:].name)
    ['foo', 'bar']
    >>> c.ownedOperation[:].formalParameter.name   # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(c.ownedOperation[:].formalParameter.name)
    ['foo', 'bar']
    >>> c.ownedOperation[0].formalParameter['it.name=="foo"', 0].name
    'foo'
    >>> c.ownedOperation[:].formalParameter['it.name=="foo"', 0].name
    'foo'
    """


class collection(object):
    """
    Collection (set-like) for model elements' 1:n and n:m relationships.
    """

    def __init__(self, property, object, type):
        self.property = property
        self.object = object
        self.type = type
        self.items = collectionlist()

    def __len__(self):
        return len(self.items)

    def __setitem__(self, key, value):
        raise RuntimeError('items should not be overwritten.')

    def __delitem__(self, key):
        self.remove(key)

    def __getitem__(self, key):
        return self.items.__getitem__(key)

    def __contains__(self, obj):
        return self.items.__contains__(obj)

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return str(self.items)

    __repr__ = __str__

    def __nonzero__(self):
        return self.items != []

    def append(self, value):
        if isinstance(value, self.type):
            self.property._set(self.object, value)
        else:
            raise TypeError('Object is not of type %s' % self.type.__name__)

    def remove(self, value):
        if value in self.items:
            self.property.__delete__(self.object, value)
        else:
            raise ValueError('%s not in collection' % value)

    def index(self, key):
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
                c += 1
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
        result = list()
        for v in self.items:
            if f(v):
                result.append(v)
        return result

    def reject(self, f):
        result = list()
        for v in self.items:
            if not f(v):
                result.append(v)
        return result

    def collect(self, f):
        result = list()
        for v in self.items:
            result.append(f(v))
        return result

    def isEmpty(self):
        return len(self.items) == 0

    def nonEmpty(self):
        return not self.isEmpty()

    def sum(self):
        r = 0
        for o in self.items:
            r = r + o
        return o

    def forAll(self, f):
        if not self.items or not inspect.getargspec(f)[0]:
            return True

        nargs = len(inspect.getargspec(f)[0])
        if inspect.getargspec(f)[3]:
            nargs -= len(inspect.getargspec(f)[3])

        assert (nargs > 0)
        nitems = len(self.items)
        index = [0] * nargs

        while 1:
            args = []
            for x in index:
                args.append(self.items[x])
            if not f(*args):
                return False
            c = len(index) - 1
            index[c] += 1
            while index[c] == nitems:
                index[c] = 0
                c = c - 1
                if c < 0:
                    return True
                else:
                    index[c] += 1
                if index[c] == nitems - 1:
                    c -= 1
        return False

    def exist(self, f):
        if not self.items or not inspect.getargspec(f)[0]:
            return False

        nargs = len(inspect.getargspec(f)[0])
        if inspect.getargspec(f)[3]:
            nargs -= len(inspect.getargspec(f)[3])

        assert (nargs > 0)
        nitems = len(self.items)
        index = [0] * nargs
        while 1:
            args = []
            for x in index:
                args.append(self.items[x])
            if f(*args):
                return True
            c = len(index) - 1
            index[c] += 1
            while index[c] == nitems:
                index[c] = 0
                c -= 1
                if c < 0:
                    return False
                else:
                    index[c] += 1
                if index[c] == nitems - 1:
                    c -= 1
        return False

    def swap(self, item1, item2):
        """
        Swap two elements. Return true if swap was successful.
        """
        try:
            i1 = self.items.index(item1)
            i2 = self.items.index(item2)
            self.items[i1], self.items[i2] = self.items[i2], self.items[i1]

            # send a notification that this list has changed
            factory = self.object.factory
            if factory:
                factory._handle(AssociationChangeEvent(self.object, self.property))
            return True
        except IndexError as ex:
            return False
        except ValueError as ex:
            return False

# vi:sw=4:et:ai
