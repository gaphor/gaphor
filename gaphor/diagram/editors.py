"""
Editors.
"""
import abc
from functools import singledispatch

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.compartment import CompartmentItem
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
    def get_bounds(self):
        """
        Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.

        Returns: a gaphas.geometry.Rectangle
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


@Editor.register(NamedItem)
class NamedItemEditor(AbstractEditor):
    """Text edit support for Named items."""

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        s = self._item.subject
        return s.name if s else ""

    def get_bounds(self):
        return None

    def update_text(self, text):
        if self._item.subject:
            self._item.subject.name = text
        self._item.request_update()

    def key_pressed(self, pos, key):
        pass


@Editor.register(DiagramItem)
class DiagramItemTextEditor(AbstractEditor):
    """Text edit support for diagram items containing text elements."""

    def __init__(self, item):
        self._item = item
        self._text_element = None

    def is_editable(self, x, y):
        if not self._item.subject:
            return False

        for txt in self._item.texts():
            if (x, y) in txt.bounds:
                self._text_element = txt
                break
        return self._text_element is not None

    def get_text(self):
        if self._text_element:
            return rgetattr(self._item.subject, self._text_element.attr)

    def get_bounds(self):
        return None

    def update_text(self, text):
        if self._text_element:
            self._text_element.text = text
            rsetattr(self._item.subject, self._text_element.attr, text)

    def key_pressed(self, pos, key):
        pass


@Editor.register(CompartmentItem)
class CompartmentItemEditor(AbstractEditor):
    """Text editor support for compartment items."""

    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """
        Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        self._edit = self._item.item_at(x, y)
        return bool(self._edit and self._edit.subject)

    def get_text(self):
        return UML.format(editable(self._edit.subject))

    def get_bounds(self):
        return None

    def update_text(self, text):
        UML.parse(editable(self._edit.subject), text)

    def key_pressed(self, pos, key):
        pass
