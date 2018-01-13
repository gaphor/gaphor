#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
This module contains some support code for queries on lists.

Two mixin classes are provided:

1. ``querymixin``
2. ``recursemixin``

See the documentation on the mixins.

"""

from __future__ import absolute_import
import six
from six.moves import filter
__all__ = [ 'querymixin', 'recursemixin', 'getslicefix' ]

import sys


class Matcher(object):
    """
    Returns True if the expression returns True.
    The context for the expression is the element.

    Given a class:

    >>> class A(object):
    ...     def __init__(self, name): self.name = name

    We can create a path for each object:

    >>> a = A('root')
    >>> a.a = A('level1')
    >>> a.b = A('b')
    >>> a.a.text = 'help'

    If we want to match, ``it`` is used to refer to the subjected object:

    >>> Matcher('it.name=="root"')(a)
    True
    >>> Matcher('it.b.name=="b"')(a)
    True
    >>> Matcher('it.name=="blah"')(a)
    False
    >>> Matcher('it.nonexistent=="root"')(a)
    False

    NOTE: the object ``it`` was introduced since properties (descriptors) can
    not be executed from within a dictionary context.
    """

    def __init__(self, expr):
        self.expr = compile(expr, '<matcher>', 'eval')

    def __call__(self, element):
        try:
            return eval(self.expr, {}, { 'it': element })
        except (AttributeError, NameError):
            # attribute does not (yet) exist
            #print 'No attribute', expr, d
            return False


class querymixin(object):
    """
    Implementation of the matcher as a mixin for lists.

    Given a class:

    >>> class A(object):
    ...     def __init__(self, name): self.name = name

    We can do nice things with this list:

    >>> class MList(querymixin, list):
    ...     pass
    >>> m = MList()
    >>> m.append(A('one'))
    >>> m.append(A('two'))
    >>> m.append(A('three'))
    >>> m[1].name
    'two'
    >>> m['it.name=="one"'] # doctest: +ELLIPSIS
    [<gaphor.misc.listmixins.A object at 0x...>]
    >>> m['it.name=="two"', 0].name
    'two'
    """

    def __getitem__(self, key):
        try:
            # See if the list can deal with it (don't change default behaviour)
            return super(querymixin, self).__getitem__(key)
        except TypeError:
            # Nope, try our matcher trick
            if type(key) is tuple:
                key, remainder = key[0], key[1:]
            else:
                remainder = None

            matcher = Matcher(key)
            matched = list(filter(matcher, self))
            if remainder:
                return type(self)(matched).__getitem__(*remainder)
            else:
                return type(self)(matched)


def issafeiterable(obj):
    """
    Checks if the object is iterable, but not a string.

    >>> issafeiterable([])
    True
    >>> issafeiterable(set())
    True
    >>> issafeiterable({})
    True
    >>> issafeiterable(1)
    False
    >>> issafeiterable('text')
    False
    """
    try:
        return iter(obj) and not isinstance(obj, six.string_types)
    except TypeError:
        pass
    return False


class recurseproxy(object):
    """
    Proxy object (helper) for the recusemixin.

    The proxy has limited capabilities compared to a real list (or set): it can
    be iterated and a getitem can be performed.
    On the other side, the type of the original sequence is maintained, so
    getitem operations act as if they're executed on the original list.
    """

    def __init__(self, sequence):
        self.__sequence = sequence

    def __getitem__(self, key):
        return self.__sequence.__getitem__(key)

    def __iter__(self):
        """
        Iterate over the items. If there is some level of nesting, the parent
        items are iterated as well.
        """
        return iter(self.__sequence)

    def __getattr__(self, key):
        """
        Create a new proxy for the attribute.
        """
        def mygetattr():
            for e in self.__sequence:
                try:
                    obj = getattr(e, key)
                    if issafeiterable(obj):
                        for i in obj:
                            yield i
                    else:
                        yield obj
                except AttributeError:
                    pass
        # Create a copy of the proxy type, inclusing a copy of the sequence type
        return type(self)(type(self.__sequence)(mygetattr()))


class recursemixin(object):
    """
    Mixin class for lists, sets, etc. If data is requested using ``[:]``,
    a ``recurseproxy`` instance is created.

    The basic idea is to have a class that can contain children:

    >>> class A(object):
    ...     def __init__(self, name, *children):
    ...         self.name = name
    ...         self.children = list(children)
    ...     def dump(self, level=0):
    ...         print ' ' * level, self.name
    ...         for c in self.children: c.dump(level+1)

    Now if we make a (complex) structure out of it:

    >>> a = A('root', A('a', A('b'), A('c'), A('d')), A('e', A('one'), A('two')))
    >>> a.dump()   # doctest: +ELLIPSIS
     root
      a
       b
       c
       d
      e
       one
       two
    >>> a.children[1].name
    'e'

    Given ``a``, I want to iterate all grand-children (b, c, d, one, two) and
    the structure I want to do that with is:

      ``a.children[:].children``

    In order to do this we have to use a special list class, so we can handle
    our specific case. ``__getslice__`` should be overridden, so we can make it
    behave like a normal python object (legacy, yes...).

    >>> class rlist(recursemixin, getslicefix, list):
    ...     pass
    >>> class A(object):
    ...     def __init__(self, name, *children):
    ...         self.name = name
    ...         self.children = rlist(children)
    ...     def dump(self, level=0):
    ...         print ' ' * level, self.name
    ...         for c in self.children: c.dump(level+1)

    >>> a = A('root', A('a', A('b'), A('c'), A('d')), A('e', A('one'), A('two')))
    >>> a.children[1].name
    'e'

    Invoking ``a.children[:]`` should now return a recurseproxy object:

    >>> a.children[:]                                       # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(a.children[:].name)                            # doctest: +ELLIPSIS
    ['a', 'e']

    Now calling a child on the list will return a list of all children:

    >>> a.children[:].children                              # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(a.children[:].children)                        # doctest: +ELLIPSIS
    [<gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>, <gaphor.misc.listmixins.A object at 0x...>]

    And of course we're interested in the names:

    >>> a.children[:].children.name                         # doctest: +ELLIPSIS
    <gaphor.misc.listmixins.recurseproxy object at 0x...>
    >>> list(a.children[:].children.name)
    ['b', 'c', 'd', 'one', 'two']
    """
    _recursemixin_trigger = slice(None, None, None)

    def proxy_class(self):
        return recurseproxy

    def __getitem__(self, key):
        if key == self._recursemixin_trigger:
            return self.proxy_class()(self)
        else:
            return super(recursemixin, self).__getitem__(key)


class getslicefix(object):
    """
    C-Python classes still use __getslice__. This behaviour is depricated
    and getitem should be called instead.
    """

    def __getslice__(self, a, b, c=None):
        """
        ``__getslice__`` is deprecated. Calls are redirected to
        ``__getitem__()``.
        """
        if a == 0: a = None
        if b == sys.maxint: b = None
        return self.__getitem__(slice(a, b, c))

# vim: sw=4:et:ai
