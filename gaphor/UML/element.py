#!/usr/bin/env python

# Copyright (C) 2001-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
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
Base class for UML model elements.
"""

from __future__ import absolute_import

import threading
import uuid

from .properties import umlproperty

__all__ = ['Element']


class Element(object):
    """
    Base class for UML data classes.
    """

    def __init__(self, id=None, factory=None):
        """
        Create an element. As optional parameters an id and factory can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well. An id False will result in no
        id being  given (for "transient" or helper classes).

        Factory can be provided to refer to the class that maintains the
        lifecycle of the element.
        """
        self._id = id or (id is not False and str(uuid.uuid1()) or False)
        # The factory this element belongs to.
        self._factory = factory
        self._unlink_lock = threading.Lock()

    id = property(lambda self: self._id, doc='Id')

    factory = property(lambda self: self._factory,
                       doc="The factory that created this element")

    def umlproperties(self):
        """
        Iterate over all UML properties 
        """
        umlprop = umlproperty
        class_ = type(self)
        for propname in dir(class_):
            if not propname.startswith('_'):
                prop = getattr(class_, propname)
                if isinstance(prop, umlprop):
                    yield prop

    def save(self, save_func):
        """
        Save the state by calling save_func(name, value).
        """
        for prop in self.umlproperties():
            prop.save(self, save_func)

    def load(self, name, value):
        """
        Loads value in name. Make sure that for every load postload()
        should be called.
        """
        try:
            prop = getattr(type(self), name)
        except AttributeError as e:
            raise AttributeError("'%s' has no property '%s'" % (type(self).__name__, name))
        else:
            prop.load(self, value)

    def postload(self):
        """
        Fix up the odds and ends.
        """
        for prop in self.umlproperties():
            prop.postload(self)

    def unlink(self):

        """Unlink the element. All the elements references are destroyed.
        
        The unlink lock is acquired while unlinking this elements properties
        to avoid recursion problems."""

        if self._unlink_lock.locked():
            return

        with self._unlink_lock:

            for prop in self.umlproperties():
                prop.unlink(self)

            if self._factory:
                self._factory._unlink_element(self)

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self, class_):
        """
        Returns true if the object is an instance of class_.
        """
        return isinstance(self, class_)

    def isTypeOf(self, other):
        """
        Returns true if the object is of the same type as other.
        """
        return type(self) == type(other)

    def __getstate__(self):
        d = dict(self.__dict__)
        try:
            del d['_factory']
        except KeyError:
            pass
        return d

    def __setstate__(self, state):
        self._factory = None
        self.__dict__.update(state)


try:
    import psyco
except ImportError:
    pass
else:
    psyco.bind(Element)

# vim:sw=4:et
