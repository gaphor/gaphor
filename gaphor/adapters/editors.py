"""
Editors.
"""
import logging
import abc
from functools import singledispatch

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.diagram.interfaces import Editor
from gaphor.misc.rattr import rgetattr, rsetattr

log = logging.getLogger(__name__)


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


@Editor.register(items.CommentItem)
class CommentItemEditor(AbstractEditor):
    """Text edit support for Comment item."""

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        return self._item.subject.body

    def get_bounds(self):
        return None

    def update_text(self, text):
        self._item.subject.body = text

    def key_pressed(self, pos, key):
        pass


@Editor.register(items.NamedItem)
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


@Editor.register(items.DiagramItem)
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
        log.debug("Updating text to %s" % text)
        if self._text_element:
            self._text_element.text = text
            rsetattr(self._item.subject, self._text_element.attr, text)

    def key_pressed(self, pos, key):
        pass


@Editor.register(items.CompartmentItem)
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


@Editor.register(items.AssociationItem)
class AssociationItemEditor(AbstractEditor):
    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        item = self._item
        if not item.subject:
            return False
        if item.head_end.point((x, y)) <= 0:
            self._edit = item.head_end
        elif item.tail_end.point((x, y)) <= 0:
            self._edit = item.tail_end
        else:
            self._edit = item
        return True

    def get_text(self):
        if self._edit is self._item:
            return self._edit.subject.name
        return UML.format(
            self._edit.subject,
            visibility=True,
            is_derived=True,
            type=True,
            multiplicity=True,
            default=True,
        )

    def get_bounds(self):
        return None

    def update_text(self, text):
        UML.parse(self._edit.subject, text)

    def key_pressed(self, pos, key):
        pass


@Editor.register(items.ForkNodeItem)
class ForkNodeItemEditor(AbstractEditor):
    """Text edit support for fork node join specification."""

    element_factory = inject("element_factory")

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        """
        Get join specification text.
        """
        if self._item.subject.joinSpec:
            return self._item.subject.joinSpec
        else:
            return ""

    def get_bounds(self):
        return None

    def update_text(self, text):
        """
        Set join specification text.
        """
        spec = self._item.subject.joinSpec
        if not spec:
            spec = text

    def key_pressed(self, pos, key):
        pass
