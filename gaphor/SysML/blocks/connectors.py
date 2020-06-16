from gaphas.connector import Handle, Port

from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.SysML import sysml
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.proxyport import ProxyPortItem


@Connector.register(BlockItem, ProxyPortItem)
class BlockProxyPortConnector:
    def __init__(self, block: BlockItem, proxy_port: ProxyPortItem,) -> None:
        assert block.canvas is proxy_port.canvas
        self.block = block
        self.proxy_port = proxy_port

    def allow(self, handle: Handle, port: Port) -> bool:
        return True

    def connect(self, handle: Handle, port: Port) -> bool:
        """
        Connect and reconnect at model level.

        Returns `True` if a connection is established.
        """
        proxy_port = self.proxy_port
        if not proxy_port.subject:
            proxy_port.subject = proxy_port.model.create(sysml.ProxyPort)
        proxy_port.subject.encapsulatedClassifier = self.block.subject

        return True

    def disconnect(self, handle: Handle) -> None:
        proxy_port = self.proxy_port
        if proxy_port.subject:
            subject = proxy_port.subject
            del proxy_port.subject
            subject.unlink()
