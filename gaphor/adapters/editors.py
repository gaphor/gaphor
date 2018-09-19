#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
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
Adapters
"""

from __future__ import absolute_import
from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor.UML import uml2, umllex
from gaphor.core import inject
from gaphor.diagram.interfaces import IEditor
from gaphor.diagram import items
from gaphor.misc.rattr import rgetattr, rsetattr
from simplegeneric import generic


@generic
def editable(el):
    """
    Return editable part of UML element.

    It returns element itself by default.
    """
    return el
    

@editable.when_type(uml2.Slot)
def editable_slot(el):
    """
    Return editable part of a slot.
    """
    return el.value


class CommentItemEditor(object):
    """
    Text edit support for Comment item.
    """
    interface.implements(IEditor)
    component.adapts(items.CommentItem)

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
    """
    Text edit support for Named items.
    """
    interface.implements(IEditor)
    component.adapts(items.NamedItem)

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        s = self._item.subject
        return s.name if s else ''

    def get_bounds(self):
        return None

    def update_text(self, text):
        if self._item.subject:
            self._item.subject.name = text
        self._item.request_update()

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(NamedItemEditor)


class DiagramItemTextEditor(object):
    """
    Text edit support for diagram items containing text elements.
    """
    interface.implements(IEditor)
    component.adapts(items.DiagramItem)

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
        log.debug('Updating text to %s' % text)
        if self._text_element:
            self._text_element.text = text
            rsetattr(self._item.subject, self._text_element.attr, text)

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(DiagramItemTextEditor)


class CompartmentItemEditor(object):
    """
    Text editor support for compartment items.
    """
    interface.implements(IEditor)
    component.adapts(items.CompartmentItem)

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
        return format(editable(self._edit.subject))

    def get_bounds(self):
        return None

    def update_text(self, text):
        umllex.parse(editable(self._edit.subject), text)

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(CompartmentItemEditor)
 

class AssociationItemEditor(object):
    interface.implements(IEditor)
    component.adapts(items.AssociationItem)

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
        return format(self._edit.subject, visibility=True,
                                is_derived=True, type=True,
                                multiplicity=True, default=True)
    def get_bounds(self):
        return None

    def update_text(self, text):
        uml2.parse(self._edit.subject, text)

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(AssociationItemEditor)
    


class ForkNodeItemEditor(object):
    """Text edit support for fork node join specification.
    """
    interface.implements(IEditor)
    component.adapts(items.ForkNodeItem)

    element_factory = inject('element_factory')

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
            return ''

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

component.provideAdapter(ForkNodeItemEditor)

# vim:sw=4:et:ai
