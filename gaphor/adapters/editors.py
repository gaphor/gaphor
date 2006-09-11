"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.diagram.interfaces import IEditor
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem


class CommentItemEditor(object):
    """Text edit support for Comment item.
    """
    interface.implements(IEditor)
    component.adapts(CommentItem)

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

component.provideAdapter(CommentItemEditor)


class NamedItemEditor(object):
    """Text edit support for Named items.
    """
    interface.implements(IEditor)
    component.adapts(NamedItem)

    def __init__(self, item):
	self._item = item

    def is_editable(self, x, y):
	return True

    def get_text(self):
	return self._item.subject.name

    def get_bounds(self):
	return None

    def update_text(self, text):
	self._item.subject.name = text

    def key_pressed(self, pos, key):
	pass

component.provideAdapter(NamedItemEditor)


class ClassifierItemEditor(object):
    interface.implements(IEditor)
    component.adapts(ClassifierItem)

    def __init__(self, item):
	self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        self._edit = None
        if y < ClassifierItem.NAME_COMPARTMENT_HEIGHT:
            self._edit = self._item
            return True
        y -= ClassifierItem.NAME_COMPARTMENT_HEIGHT
        for comp in self._item.compartments:
            y -= comp.MARGIN_Y
            for item in comp:
                if y < item.height:
                    self._edit = item
                    return True
                y -= item.height
            y -= comp.MARGIN_Y
	return False

    def get_text(self):
        if hasattr(self._edit.subject, 'render'):
            return self._edit.subject.render()
	return self._edit.subject.name

    def get_bounds(self):
	return None

    def update_text(self, text):
        if hasattr(self._edit.subject, 'parse'):
            return self._edit.subject.parse(text)
        else:
            self._item.subject.name = text


    def key_pressed(self, pos, key):
	pass

component.provideAdapter(ClassifierItemEditor)
    

# vim:sw=4:et:ai
