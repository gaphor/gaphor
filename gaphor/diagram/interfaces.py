#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
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
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnect
   Use to define adapters for connecting 
 - IEditor
   Text editor interface

"""


from __future__ import absolute_import
from zope import interface


class IEditor(interface.Interface):
    """
    Provide an interface for editing text with the TextEditTool.
    """

    def is_editable(self, x, y):
        """
        Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        (this method should be called before get_text() is called.
        """

    def get_text(self):
        """
        Get the text to be updated
        """

    def get_bounds(self):
        """
        Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.

        Returns: a gaphas.geometry.Rectangle
        """

    def update_text(self, text):
        """
        Update with the new text.
        """

    def key_pressed(self, pos, key):
        """
        Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """

class IConnect(interface.Interface):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    def connect(self, handle, port):
        """
        Connect a line's handle to element.

        Note that at the moment of the connect, handle.connected_to may point
        to some other item. The implementor should do the disconnect of
        the other element themselves.
        """

    def disconnect(self, handle):
        """
        The true disconnect. Disconnect a handle.connected_to from an
        element. This requires that the relationship is also removed at
        model level.
        """

    def connect_constraints(self, handle):
        """
        Connect a handle to the element.
        """

    def disconnect_constraints(self, handle):
        """
        Disconnect a line's handle from an element.
        This is called whenever a handle is dragged.
        """

    def glue(self, handle):
        """
        Determine if a handle can glue to a specific element.

        Returns a tuple (x, y) if the line and element may connect, None
        otherwise.
        """


class IGroup(interface.Interface):
    """
    Provide interface for adding one UML object to another, i.e.
    interactions contain lifelines and components contain classes objects.
    """

    def pre_can_contain(self):
        """
        Determine if parent can contain item, which is instance of given
        class. Method called before item creation.
        """

    def can_contain(self):
        """
        Determine if parent can contain item.
        """

    def group(self):
        """
        Perform grouping of items.
        """

    def ungroup(self):
        """
        Perform ungrouping of items.
        """


# vim: sw=4:et:ai
