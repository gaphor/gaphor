#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Interface item related connections.

The connectors implemented in this module check if connection is possible
to folded interface, see `gaphor.diagram.classes.interface` documentation
for details.
"""

from __future__ import absolute_import
from zope import interface, component
from gaphor.diagram import items
from gaphor.adapters.classes.classconnect import DependencyConnect, ImplementationConnect

class ImplementationInterfaceConnect(ImplementationConnect):
    """
    Connect interface item and a behaviored classifier using an
    implementation.
    """
    component.adapts(items.InterfaceItem, items.ImplementationItem)

    def connect(self, handle, port):
        """
        Implementation item can be changed to draw in solid mode, when
        connected to folded interface.
        """
        super(ImplementationInterfaceConnect, self).connect(handle, port)
        if handle is self.line.head:
            self.line._solid = self.element.folded != self.element.FOLDED_NONE


    def disconnect(self, handle):
        """
        If implementation item is no longer connected to an interface, then
        draw it in non-solid mode.
        """
        super(ImplementationInterfaceConnect, self).disconnect(handle)
        if handle is self.line.head:
            self.line._solid = False


component.provideAdapter(ImplementationInterfaceConnect)



class DependencyInterfaceConnect(DependencyConnect):
    """
    Connect interface item with dependency item.
    """
    component.adapts(items.InterfaceItem, items.DependencyItem)

    def connect(self, handle, port):
        """
        Dependency item is changed to draw in solid mode, when connected to
        folded interface.
        """
        super(DependencyInterfaceConnect, self).connect(handle, port)
        line = self.line
        # connecting to the interface, which is supplier - assuming usage
        # dependency
        if handle is line.head:
            if self.element.folded != self.element.FOLDED_NONE:
                line._solid = True
                self.element.folded = self.element.FOLDED_REQUIRED
            # change interface angle even when it is unfolded, this way
            # required interface will be rotated properly when folded by
            # user
            self.element._angle = port.angle


    def disconnect(self, handle):
        """
        If dependency item is no longer connected to an interface, then
        draw it in non-solid mode. Interface's folded mode changes to
        provided (ball) notation.
        """
        super(DependencyInterfaceConnect, self).disconnect(handle)
        if handle is self.line.head:
            iface = self.element
            self.line._solid = False
            # don't change folding notation when interface is unfolded, see
            # test_unfolded_interface_disconnection as well
            if iface.folded:
                iface.folded = iface.FOLDED_PROVIDED


component.provideAdapter(DependencyInterfaceConnect)

# vim:sw=4:et:ai
