"""Containment connection adapters."""

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.presentation import ElementPresentation
from gaphor.UML.classes.containment import ContainmentItem
from gaphor.UML.recipes import owner_package


@Connector.register(ElementPresentation, ContainmentItem)
class ContainmentConnect(BaseConnector):
    """Connect a containment relationship to elements that can be nested.

    Head is the container, tail connects to the contained item.
    """

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

    def container_and_contained_element(self, handle):
        line = self.line
        opposite = line.opposite(handle)
        connected_to = self.get_connected(opposite)
        if not (connected_to and connected_to.subject):
            return None, None
        elif handle is line.head:
            return self.element.subject, connected_to.subject
        else:
            return connected_to.subject, self.element.subject

    def connect(self, handle, port) -> bool:
        container, contained = self.container_and_contained_element(handle)
        if isinstance(container, UML.Package) and isinstance(
            contained, (UML.Type, UML.Package)
        ):
            contained.package = container
            return True
        if isinstance(container, UML.Package) and isinstance(contained, (Diagram)):
            contained.element = container
            return True
        elif isinstance(container, UML.Class) and isinstance(contained, UML.Classifier):
            del contained.package
            contained.nestingClass = container
            return True
        return False

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        oct = self.get_connected(opposite)
        hct = self.get_connected(handle)

        if hct and oct:
            if hct.subject in oct.subject.ownedElement:
                assert isinstance(hct.subject, (UML.Type, UML.Package))
                if isinstance(hct.subject, UML.Classifier):
                    del hct.subject.nestingClass
                hct.subject.package = owner_package(hct.diagram.owner)
            if oct.subject in hct.subject.ownedElement:
                assert isinstance(oct.subject, (UML.Type, UML.Package))
                if isinstance(oct.subject, UML.Classifier):
                    del oct.subject.nestingClass
                oct.subject.package = owner_package(oct.diagram.owner)

        super().disconnect(handle)
