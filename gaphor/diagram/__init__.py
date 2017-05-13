#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
The diagram package contains items (to be drawn on the diagram), tools
(used for interacting with the diagram) and interfaces (used for adapting the
diagram).
"""

from __future__ import absolute_import
import inspect
import gobject
import uuid

from gaphor.diagram.style import Style
import six

# Map UML elements to their (default) representation.
_uml_to_item_map = { }

def create(type):
    return create_as(type, str(uuid.uuid1()))

def create_as(type, id):
    return type(id)

def get_diagram_item(element):
    global _uml_to_item_map
    return _uml_to_item_map.get(element)

def set_diagram_item(element, item):
    global _uml_to_item_map
    _uml_to_item_map[element] = item


def uml(uml_class, stereotype=None):
    """
    Assign UML metamodel class and a stereotype to diagram item.

    :Parameters:
     uml_class
        UML metamodel class.
     stereotype
        Stereotype name (i.e. 'subsystem').
    """
    def f(item_class):
        t = uml_class
        if stereotype is not None:
            t = (uml_class, stereotype)
            item_class.__stereotype__ = stereotype
        set_diagram_item(t, item_class)
        return item_class
    return f



class DiagramItemMeta(type):
    """
    Initialize a new diagram item.
    1. Register UML.Elements by means of the __uml__ attribute (see
       map_uml_class method).
    2. Set items style information.

    @ivar style: style information
    """

    def __init__(self, name, bases, data):
        type.__init__(self, name, bases, data)

        self.map_uml_class(data)
        self.set_style(data)


    def map_uml_class(self, data):
        """
        Map UML class to diagram item.

        @param cls:  new instance of item class
        @param data: metaclass data with UML class information 

        """
        if '__uml__' in data:
            obj = data['__uml__']
            if isinstance(obj, (tuple, set, list)):
                for c in obj:
                    set_diagram_item(c, self)
            else:
                set_diagram_item(obj, self)


    def set_style(self, data):
        """
        Set item style information by merging provided information with
        style information from base classes.

        @param cls:   new instance of diagram item class
        @param bases: base classes of an item
        @param data:  metaclass data with style information
        """
        style = Style()
        for c in self.__bases__:
            if hasattr(c, 'style'):
                for (name, value) in c.style.items():
                    style.add(name, value)

        if '__style__' in data:
            for (name, value) in six.iteritems(data['__style__']):
                style.add(name, value)

        self.style = style


# vim:sw=4:et
