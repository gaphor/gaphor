from gaphas.connector import Handle, Port

from gaphor import UML
from gaphor.diagram.connectors import Connector, RelationshipConnect
from gaphor.SysML import sysml
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.constraintparameter import ConstraintParameterItem
from gaphor.SysML.blocks.constraintproperty import ConstraintPropertyItem
from gaphor.SysML.blocks.interfaceblock import InterfaceBlockItem
from gaphor.SysML.blocks.property import PropertyItem
from gaphor.SysML.blocks.proxyport import ProxyPortItem
from gaphor.SysML.diagramtype import DiagramFrameItem
from gaphor.UML.deployments import ConnectorItem


@Connector.register(ConstraintPropertyItem, ConstraintParameterItem)
class ConstraintPropertyParameterConnector:
    def __init__(
        self,
        element: ConstraintPropertyItem,
        parameter: ConstraintParameterItem,
    ) -> None:
        self.element = element
        self.parameter = parameter

    def allow(self, handle: Handle, port: Port) -> bool:
        element = self.element
        parameter = self.parameter

        if not (element.subject and parameter.subject):
            return False

        # Parameter can be attached to a constraint property, if the property
        # is typed by the constraint block that owns the parameter.
        return (
            isinstance(element.subject, UML.Property)
            and parameter.subject.owner is element.subject.type
        )

    def connect(self, handle: Handle, port: Port) -> bool:
        """Connect and reconnect at model level."""
        self.parameter.change_parent(self.element)
        return True

    def disconnect(self, handle: Handle) -> None:
        """
        Do not allow disconnection of a ConstraintParameterItem from a
        ConstraintPropertyItem.
        """
        pass


@Connector.register(InterfaceBlockItem, ProxyPortItem)
@Connector.register(BlockItem, ProxyPortItem)
@Connector.register(PropertyItem, ProxyPortItem)
@Connector.register(DiagramFrameItem, ProxyPortItem)
class BlockProperyProxyPortConnector:
    def __init__(
        self,
        element: BlockItem | PropertyItem | DiagramFrameItem | InterfaceBlockItem,
        proxy_port: ProxyPortItem,
    ) -> None:
        self.element = element
        self.proxy_port = proxy_port

    def allow(self, handle: Handle, port: Port) -> bool:
        # Early return when diagrams are not the same
        if (
            not bool(self.element.diagram)
            or self.element.diagram is not self.proxy_port.diagram
        ):
            return False

        if isinstance(self.element, DiagramFrameItem):
            # Allow only on blocks
            return isinstance(self.element.subject, sysml.Block) and isinstance(
                self.element.subject, UML.EncapsulatedClassifier
            )
        else:
            return (
                isinstance(self.element.subject, UML.EncapsulatedClassifier)
                or isinstance(self.element.subject, UML.Property)
                and isinstance(self.element.subject.type, UML.EncapsulatedClassifier)
            )

    def connect(self, handle: Handle, port: Port) -> bool:
        """Connect and reconnect at model level.

        Returns `True` if a connection is established.
        """
        proxy_port = self.proxy_port
        if not proxy_port.subject:
            proxy_port.subject = proxy_port.model.create(sysml.ProxyPort)

        if isinstance(self.element.subject, UML.EncapsulatedClassifier):
            proxy_port.subject.encapsulatedClassifier = self.element.subject
        elif isinstance(self.element.subject, UML.Property) and isinstance(
            self.element.subject.type, UML.EncapsulatedClassifier
        ):
            proxy_port.subject.encapsulatedClassifier = self.element.subject.type

        # This raises the item in the item hierarchy
        assert proxy_port.diagram
        assert self.element.diagram is proxy_port.diagram
        proxy_port.change_parent(self.element)

        return True

    def disconnect(self, handle: Handle) -> None:
        proxy_port = self.proxy_port
        if proxy_port.subject and proxy_port.diagram:
            proxy_port.change_parent(None)
            proxy_port.subject = None


@Connector.register(ProxyPortItem, ConnectorItem)
@Connector.register(PropertyItem, ConnectorItem)
@Connector.register(ConstraintParameterItem, ConnectorItem)
class PropertyConnectorConnector(RelationshipConnect):
    """Connect a Connector to a Port or Property."""

    line: ConnectorItem
    element: PropertyItem | ProxyPortItem | ConstraintParameterItem

    def allow(self, handle, port):
        element = self.element

        # Element should be connected -> have a subject
        return super().allow(handle, port) and isinstance(
            element.subject, UML.Port | UML.Property
        )

    def connect_subject(self, handle):
        line = self.line

        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if c1 and c2 and not line.subject:
            assert isinstance(c1.subject, UML.ConnectableElement)
            assert isinstance(c2.subject, UML.ConnectableElement)
            connector = UML.recipes.create_connector(c1.subject, c2.subject)
            line.subject = connector

            # Traverse the presentation hierarchy to find the structured classifier
            owner_item = c1
            while owner_item and not isinstance(
                owner_item.subject, UML.StructuredClassifier
            ):
                owner_item = owner_item.parent

            if owner_item:
                owner = owner_item.subject
                assert isinstance(owner, UML.StructuredClassifier)
                connector.structuredClassifier = owner
