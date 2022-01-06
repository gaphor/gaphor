from typing import Union

from gaphas.connector import Handle, Port

from gaphor import UML
from gaphor.diagram.connectors import Connector, UnaryRelationshipConnect
from gaphor.SysML import sysml
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.property import PropertyItem
from gaphor.SysML.blocks.proxyport import ProxyPortItem
from gaphor.UML.components import ConnectorItem


@Connector.register(BlockItem, ProxyPortItem)
@Connector.register(PropertyItem, ProxyPortItem)
class BlockProperyProxyPortConnector:
    def __init__(
        self,
        block: Union[BlockItem, PropertyItem],
        proxy_port: ProxyPortItem,
    ) -> None:
        assert block.diagram is proxy_port.diagram
        self.block = block
        self.proxy_port = proxy_port

    def allow(self, handle: Handle, port: Port) -> bool:
        return True

    def connect(self, handle: Handle, port: Port) -> bool:
        """Connect and reconnect at model level.

        Returns `True` if a connection is established.
        """
        proxy_port = self.proxy_port
        if not proxy_port.subject:
            proxy_port.subject = proxy_port.model.create(sysml.ProxyPort)
        if isinstance(self.block.subject, UML.EncapsulatedClassifier):
            proxy_port.subject.encapsulatedClassifier = self.block.subject

        # This raises the item in the item hierarchy
        assert proxy_port.diagram
        proxy_port.change_parent(self.block)

        return True

    def disconnect(self, handle: Handle) -> None:
        proxy_port = self.proxy_port
        if proxy_port.subject and proxy_port.diagram:
            subject = proxy_port.subject
            del proxy_port.subject
            proxy_port.change_parent(None)
            subject.unlink()


@Connector.register(ProxyPortItem, ConnectorItem)
@Connector.register(PropertyItem, ConnectorItem)
class PropertyConnectorConnector(UnaryRelationshipConnect):
    """Connect a Connector to a Port or Property."""

    line: ConnectorItem
    element: Union[PropertyItem, ProxyPortItem]

    def allow(self, handle, port):
        element = self.element

        # Element should be connected -> have a subject
        if not isinstance(element.subject, (UML.Port, UML.Property)):
            return None

        return super().allow(handle, port)

    def connect_subject(self, handle):
        line = self.line

        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if c1 and c2 and not line.subject:
            assert isinstance(c1.subject, UML.ConnectableElement)
            assert isinstance(c2.subject, UML.ConnectableElement)
            connector = UML.recipes.create_connector(c1.subject, c2.subject)
            line.subject = connector
            connector.structuredClassifier = c1.subject.owner or c2.subject.owner
