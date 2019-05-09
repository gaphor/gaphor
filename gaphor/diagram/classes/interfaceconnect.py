"""
Interface item related connections.

The connectors implemented in this module check if connection is possible
to folded interface, see `gaphor.diagram.classes.interface` documentation
for details.
"""

from gaphor import UML

from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect
from .classconnect import DependencyConnect, ImplementationConnect


@IConnect.register(items.InterfaceItem, items.ImplementationItem)
class ImplementationInterfaceConnect(ImplementationConnect):
    """Connect interface item and a behaviored classifier using an
    implementation.
    """

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


@IConnect.register(items.InterfaceItem, items.DependencyItem)
class DependencyInterfaceConnect(DependencyConnect):
    """Connect interface item with dependency item."""

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
