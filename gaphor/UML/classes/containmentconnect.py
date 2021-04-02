"""Containment connection adapters."""

from gaphor import UML
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.presentation import ElementPresentation
from gaphor.UML.classes.containment import ContainmentItem


@Connector.register(ElementPresentation, ContainmentItem)
class ContainmentConnect(BaseConnector):
    """Connect a containment relationship to elements that can be nested."""

    line: ContainmentItem

    def allow(self, handle, port):
        """In addition to the normal check, both line ends may not be connected
        to the same element."""
        opposite = self.line.opposite(handle)
        connected_to = self.get_connected(opposite)
        element = self.element

        if connected_to is element:
            return None

        # Same goes for subjects:
        if (
            connected_to
            and not connected_to.subject
            and not element.subject
            and connected_to.subject is element.subject
        ):
            return None

        return super().allow(handle, port)

    def connect(self, handle, port):
        if super().connect(handle, port):
            opposite = self.line.opposite(handle)
            connected_to = self.get_connected(opposite)
            if connected_to and connected_to.subject:
                if isinstance(connected_to.subject, UML.Package):
                    connected_to.subject.ownedElement = self.element.subject
                else:
                    assert isinstance(self.element.subject, UML.Package)
                    self.element.subject.ownedElement = connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        oct = self.get_connected(opposite)
        hct = self.get_connected(handle)

        if hct and oct:
            if hct.subject:
                del oct.subject.ownedElement[hct.subject]
            elif oct.subject:
                del hct.subject.ownedElement[oct.subject]

        super().disconnect(handle)
