"""Containment connection adapters."""

from gaphor import UML
from gaphor.core.modeling import Diagram, self_and_owners
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.group import group, ungroup
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
        container, contained = self.container_and_contained_element(handle)

        if not container or not contained:
            return True

        if contained in self_and_owners(container):
            return False

        return super().allow(handle, port) and (
            isinstance(container, UML.Package)
            and isinstance(contained, (UML.Type, UML.Package))
            or isinstance(container, UML.Package)
            and isinstance(contained, (Diagram))
            or isinstance(container, UML.Class)
            and isinstance(contained, UML.Classifier)
        )

    def container_and_contained_element(self, handle):
        line = self.line
        opposite = line.opposite(handle)
        connected_to = self.get_connected(opposite)
        if not (connected_to and connected_to.subject):
            return None, None
        elif handle is line.head:
            return self.element.subject, connected_to.subject
        return connected_to.subject, self.element.subject

    def connect(self, handle, port) -> bool:
        container, contained = self.container_and_contained_element(handle)
        return group(container, contained) if container and contained else False  # type: ignore[no-any-return]

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        oct = self.get_connected(opposite)
        hct = self.get_connected(handle)

        if hct and oct:
            if oct.subject and hct.subject in oct.subject.ownedElement:
                assert isinstance(hct.subject, (UML.Type, UML.Package))
                ungroup(oct.subject, hct.subject)
                hct.subject.package = owner_package(hct.diagram.owner)
            if hct.subject and oct.subject in hct.subject.ownedElement:
                assert isinstance(oct.subject, (UML.Type, UML.Package))
                ungroup(hct.subject, oct.subject)
                oct.subject.package = owner_package(oct.diagram.owner)

        super().disconnect(handle)
