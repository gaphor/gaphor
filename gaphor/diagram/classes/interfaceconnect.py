"""
Interface item related connections.

The connectors implemented in this module check if connection is possible
to folded interface, see `gaphor.diagram.classes.interface` documentation
for details.
"""


from gaphor.diagram.classes.classconnect import DependencyConnect, ImplementationConnect
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.implementation import ImplementationItem
from gaphor.diagram.classes.interface import Folded, InterfaceItem
from gaphor.diagram.connectors import IConnect


@IConnect.register(InterfaceItem, ImplementationItem)
class ImplementationInterfaceConnect(ImplementationConnect):
    """Connect interface item and a behaviored classifier using an
    implementation.
    """

    def connect(self, handle, port):
        """
        Implementation item can be changed to draw in solid mode, when
        connected to folded interface.
        """
        super().connect(handle, port)
        if handle is self.line.head:
            self.line.request_update()

    def disconnect(self, handle):
        """
        If implementation item is no longer connected to an interface, then
        draw it in non-solid mode.
        """
        super().disconnect(handle)
        if handle is self.line.head:
            self.line.request_update()


@IConnect.register(InterfaceItem, DependencyItem)
class DependencyInterfaceConnect(DependencyConnect):
    """Connect interface item with dependency item."""

    def connect(self, handle, port):
        """
        Dependency item is changed to draw in solid mode, when connected to
        folded interface.
        """
        super().connect(handle, port)
        line = self.line
        # connecting to the interface, which is supplier - assuming usage
        # dependency
        if handle is line.head:
            # change interface side even when it is unfolded, this way
            # required interface will be rotated properly when folded by
            # user
            self.element.side = port.side
            self.element.request_update()
            self.line.request_update()

    def disconnect(self, handle):
        """
        If dependency item is no longer connected to an interface, then
        draw it in non-solid mode. Interface's folded mode changes to
        provided (ball) notation.
        """
        super().disconnect(handle)
        if handle is self.line.head:
            self.element.request_update()
            self.line.request_update()
