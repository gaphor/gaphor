"""
Editors.
"""
import abc
from functools import singledispatch

from gaphor import UML
from gaphor.diagram.presentation import Named, Classified
from gaphor.misc.rattr import rgetattr, rsetattr


@singledispatch
def Editor(obj):
    pass


@singledispatch
def editable(el):
    """
    Return editable part of UML element.

    It returns element itself by default.
    """
    return el


@editable.register(UML.Slot)
def editable_slot(el):
    """
    Return editable part of a slot.
    """
    return el.value


class AbstractEditor(metaclass=abc.ABCMeta):
    """
    Provide an interface for editing text with the TextEditTool.
    """

    @abc.abstractmethod
    def is_editable(self, x, y):
        """
        Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        (this method should be called before get_text() is called.
        """

    @abc.abstractmethod
    def get_text(self):
        """
        Get the text to be updated
        """

    @abc.abstractmethod
    def update_text(self, text):
        """
        Update with the new text.
        """

    @abc.abstractmethod
    def key_pressed(self, pos, key):
        """
        Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """


@Editor.register(Named)
class NamedItemEditor(AbstractEditor):
    """Text edit support for Named items."""

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        s = self._item.subject
        return s.name if s else ""

    def update_text(self, text):
        if self._item.subject:
            self._item.subject.name = text
        self._item.request_update()

    def key_pressed(self, pos, key):
        pass


# TODO: Needs implementing
@Editor.register(Classified)
class ClassifiedItemEditor(AbstractEditor):
    """Text editor support for compartment items."""

    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """
        Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        self._edit = hasattr(self._item, "item_at") and self._item.item_at(x, y)
        return bool(self._edit)

    def get_text(self):
        return UML.format(editable(self._edit.subject))

    def update_text(self, text):
        UML.parse(editable(self._edit.subject), text)

    def key_pressed(self, pos, key):
        pass
