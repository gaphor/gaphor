#!/usr/bin/env python
"""
Base class for UML model elements.
"""

__all__ = ["Element"]

import uuid

from gaphor.UML.properties import umlproperty
from gaphor.UML.elementdispatcher import EventWatcher


class UnlinkEvent:
    """Used to tell event handlers this element should be unlinked.
    """

    def __init__(self, element):
        self.element = element


class Element:
    """
    Base class for UML data classes.
    """

    def __init__(self, id=None, model=None):
        """
        Create an element. As optional parameters an id and model can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well. An id False will result in no
        id being  given (for "transient" or helper classes).

        A model can be provided to refer to the model this element belongs to.
        """
        self._id = id or (id is not False and str(uuid.uuid1()) or False)
        # The model this element belongs to.
        self._model = model
        self._unlink_lock = 0

    id = property(lambda self: self._id, doc="Id")

    model = property(lambda self: self._model, doc="the owning model")

    def umlproperties(self):
        """
        Iterate over all UML properties
        """
        umlprop = umlproperty
        class_ = type(self)
        for propname in dir(class_):
            if not propname.startswith("_"):
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
            raise AttributeError(
                "'%s' has no property '%s'" % (type(self).__name__, name)
            )
        else:
            prop.load(self, value)

    def postload(self):
        """
        Fix up the odds and ends.
        """
        for prop in self.umlproperties():
            prop.postload(self)

    def unlink(self):
        """
        Unlink the element. All the elements references are destroyed.

        The unlink lock is acquired while unlinking this elements properties
        to avoid recursion problems."""

        if self._unlink_lock:
            return

        try:
            self._unlink_lock += 1

            for prop in self.umlproperties():

                prop.unlink(self)

            self.handle(UnlinkEvent(self))
        finally:
            self._unlink_lock -= 1

    def handle(self, event):
        """
        Propagate incoming events
        """
        model = self._model
        if model:
            model.handle(event)

    def watcher(self, default_handler=None):
        return EventWatcher(self, default_handler)

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self, class_):
        """
        Returns true if the object is an instance of `class_`.
        """
        return isinstance(self, class_)

    def isTypeOf(self, other):
        """
        Returns true if the object is of the same type as other.
        """
        return isinstance(self, type(other))
