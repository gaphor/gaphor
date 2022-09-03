"""Connector connections.

Implemented using interface item in assembly connector mode, see
`gaphor.diagram.connector` module for details.
"""

from typing import Union

from gaphor import UML
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.classes.interface import InterfaceItem
from gaphor.UML.deployments.connector import ConnectorItem


@Connector.register(ComponentItem, ConnectorItem)
@Connector.register(InterfaceItem, ConnectorItem)
class LegacyConnectorConnectBase(BaseConnector):
    """This connector is left as is, mainly for backwards compatibility.

    The Connector item has been removed from the Components tool
    palette.
    """

    element: Union[ComponentItem, InterfaceItem]
    line: ConnectorItem

    def get_connecting(self, iface, both=False):
        """Get items connecting to interface.

        :Parameters:
         iface
            Interface in question.
         both
            If true, then filter out one-side connections.
        """
        diagram = iface.diagram
        connected = diagram.connections.get_connections(connected=iface)
        if both:
            connected = [
                c
                for c in connected
                if diagram.connections.get_connection(c.item.opposite(c.handle))
            ]
        return connected

    @staticmethod
    def get_component(connector):
        """Get component connected by connector."""
        diagram = connector.diagram
        c1 = diagram.connections.get_connection(connector.head)
        c2 = diagram.connections.get_connection(connector.tail)
        component = None
        if c1 and isinstance(c1.connected, ComponentItem):
            component = c1.connected
        elif c2 and isinstance(c2.connected, ComponentItem):
            component = c2.connected
        return component

    def create_uml(self, connector, component, assembly, iface):
        """Create assembly connector UML metamodel for given connector item and
        component.

        :Parameters:
         connector
            Connector item.
         component
            Component item.
         assembly
            Instance of Connector UML metaclass.
         iface
            Instance of Interface UML metaclass.
        """
        connector.subject = assembly

        end = connector.model.create(UML.ConnectorEnd)
        end.role = iface
        end.partWithPort = connector.model.create(UML.Port)
        assembly.end = end

        component.subject.ownedPort = end.partWithPort

    def drop_uml(self, connector, component):
        """Destroy assembly connector UML metamodel existing between connector
        item and component item.

        :Parameters:
         connector
            Connector item.
         component
            Component item.
        """
        if component and component.subject:
            p = component.subject.ownedPort[0]
            p.unlink()
            connector.subject = None

    def allow(self, handle, port):
        iface = self.element
        component = self.get_connected(self.line.opposite(handle))

        if isinstance(component, InterfaceItem) or isinstance(iface, ComponentItem):
            component, iface = iface, component
        # connect only components and interfaces but not two interfaces nor
        # two components
        glue_ok = (not component or isinstance(component, ComponentItem)) and (
            not iface or isinstance(iface, InterfaceItem)
        )

        return glue_ok and super().allow(handle, port)

    def connect(self, handle, port):
        super().connect(handle, port)

        line = self.line

        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if c1 and c2:
            # reference interface and component correctly
            iface = c1
            component = c2
            if isinstance(component, InterfaceItem):
                assert isinstance(iface, ComponentItem)
                component, iface = iface, component

            connections = self.get_connecting(iface, both=True)

            assembly = None
            for c in connections:
                if c.item.subject:
                    assembly = c.item.subject
                    assert assembly.kind == "assembly"
                    break

            if line.subject:
                assert isinstance(line.subject, UML.Connector)
                assembly = line.subject
                assert assembly.end
                assert list(assembly.end[:].partWithPort)
                assert iface.subject in assembly.end[:].role
                return

            if assembly is None:
                assembly = self.element.model.create(UML.Connector)
                assembly.kind = "assembly"
                for c in connections:
                    connector = c.item
                    self.create_uml(
                        connector,
                        self.get_component(connector),
                        assembly,
                        iface.subject,
                    )
            else:
                self.create_uml(line, component, assembly, iface.subject)
            iface.request_update()

    def disconnect(self, handle):
        super().disconnect(handle)
        line = self.line
        if line.subject is None:
            return

        iface = self.get_connected(line.head)
        if not isinstance(iface, InterfaceItem):
            iface = self.get_connected(line.tail)

        assert iface, "No interface found on {line}"

        connections = list(self.get_connecting(iface, both=True))

        # destroy whole assembly if one connected item stays
        # or only one port will stay connected
        if len(connections) == 2:
            connector = line.subject
            for ci in connections:
                c = self.get_component(ci.item)
                self.drop_uml(ci.item, c)
                line.request_update()
            connector.unlink()
        else:
            c = self.get_component(line)
            self.drop_uml(line, c)
        iface.request_update()
