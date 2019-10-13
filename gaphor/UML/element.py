#!/usr/bin/env python
"""
Base class for UML model elements.
"""

from __future__ import annotations

__all__ = ["Element"]

import uuid

from typing import Optional, Sequence, TYPE_CHECKING, Type, Union
from gaphor.UML.properties import umlproperty
from gaphor.UML.elementdispatcher import EventWatcher

if TYPE_CHECKING:
    from gaphor.UML.elementfactory import ElementFactory  # noqa
    from gaphor.UML.presentation import Presentation  # noqa


class UnlinkEvent:
    """Used to tell event handlers this element should be unlinked.
    """

    def __init__(self, element: Element):
        self.element = element


Id = Union[str, bool]


class Element:
    """
    Base class for UML data classes.
    """

    def __init__(
        self, id: Optional[Id] = None, model: Optional["ElementFactory"] = None
    ):
        """
        Create an element. As optional parameters an id and model can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well. An id False will result in no
        id being  given (for "transient" or helper classes).

        A model can be provided to refer to the model this element belongs to.
        """
        super().__init__()
        self._id: Id = id or (id is not False and str(uuid.uuid1()) or False)
        # The model this element belongs to.
        self._model = model
        self._unlink_lock = 0

    @property
    def id(self) -> Id:
        "Id"
        return self._id

    @property
    def model(self) -> "ElementFactory":
        "The owning model, raises AssertionError when model is not set."
        assert (
            self._model
        ), "You can not retrieve the model since it's not set on construction"
        return self._model

    appliedStereotype: umlproperty[Element, Sequence[Element]]
    owner: umlproperty[Element, Sequence[Element]]
    ownedComment: umlproperty[Element, Sequence[Element]]
    ownedElement: umlproperty[Element, Sequence[Element]]
    presentation: umlproperty["Presentation", Sequence["Presentation"]]

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
            raise AttributeError(f"'{type(self).__name__}' has no property '{name}'")
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
        dispatcher = self._model.element_dispatcher if self._model else None
        return EventWatcher(self, dispatcher, default_handler)

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self, class_: Type[Element]):
        """
        Returns true if the object is an instance of `class_`.
        """
        return isinstance(self, class_)

    def isTypeOf(self, other: Element):
        """
        Returns true if the object is of the same type as other.
        """
        return isinstance(self, type(other))
