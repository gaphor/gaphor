#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
Interfaces related to the user interface.
"""

from __future__ import absolute_import
from zope import interface


class IDiagramTabChange(interface.Interface):
    """
    The selected diagram changes.
    """
    item = interface.Attribute('The newly selected DockItem')

    diagram_tab = interface.Attribute('The newly selected diagram tab')

class IDiagramSelectionChange(interface.Interface):
    """
    The selection of a diagram changed.
    """
    diagram_view = interface.Attribute('The diagram View that emits the event')

    focused_item = interface.Attribute('The diagram item that received focus')

    selected_items = interface.Attribute('All selected items in the diagram')


class IUIComponent(interface.Interface):
    """
    A user interface component.
    """
    
    ui_name = interface.Attribute('The UIComponent name, provided by the loader')

    title = interface.Attribute('Title of the component')

    size = interface.Attribute('Size used for floating the component')

    placement = interface.Attribute('placement. E.g. ("left", "diagrams")')

    def open(self):
        """
        Create and display the UI components (windows).
        """

    def close(self):
        """
        Close the UI component. The component can decide to hide or destroy the UI
        components.
        """


class IPropertyPage(interface.Interface):
    """
    A property page which can display itself in a notebook
    """
    
    order = interface.Attribute('Order number, used for ordered display')

    def construct(self):
        """
        Create the page (gtk.Widget) that belongs to the Property page.

        Returns the page's toplevel widget (gtk.Widget).
        """

    def destroy(self):
        """
        Destroy the page and clean up signal handlers and stuff.
        """


# vim:sw=4:et:ai
