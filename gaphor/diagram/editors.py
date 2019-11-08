"""
Editors.
"""
import abc
from functools import singledispatch

from gaphor import UML
from gaphor.diagram.presentation import Named, Classified


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
