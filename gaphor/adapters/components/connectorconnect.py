"""
Connector connections.

Currently, two kind of connections are supported. First one is simple
assembly connector between two components. Second allows to visually group
assembly connectors (see UML 2.2 specification, figure 8.18, page 160) by
connecting component and other assembly connector.
"""

import operator

from zope import interface, component

from gaphor import UML
from gaphor.diagram import items
from gaphor.adapters.connectors import AbstractConnect


class ConnectorConnectBase(AbstractConnect):
    def _get_interfaces(self, c1, c2):
        """
        Return list of common interfaces provided by first component and
        required by second component.

        :Parameters:
         c1
            Component providing interfaces.
         c2
            Component requiring interfaces.
        """
        provided = set(c1.subject.provided)
        required = set(c2.subject.required)
        interfaces = list(provided.intersection(required))
        interfaces.sort(key=operator.attrgetter('name'))
        return interfaces


    def _get_info(self, assembly):
        data = {
            'required': [],
            'provided': [],
            'interfaces': [],
        }
        return data


    def connect(self, handle, port):
        super(ConnectorConnectBase, self).connect(handle, port)

        line = self.line
        assembly = line.head.connected_to
        if not isinstance(assembly, items.AssemblyConnectorItem):
            assembly = line.tail.connected_to

        if isinstance(assembly, items.AssemblyConnectorItem):
            data = self._get_info(assembly)

            if data['interfaces']:
                # create uml data model
                connector = line.subject = self.element_factory.create(UML.Connector)
                end1 = self.element_factory.create(UML.ConnectorEnd)
                end2 = self.element_factory.create(UML.ConnectorEnd)
                interface = self._get_interfaces(provided, required)[0]
                end1.role = interface
                end2.role = interface
                connector.end = end1
                connector.end = end2
                p1 = self.element_factory.create(UML.Port)
                p2 = self.element_factory.create(UML.Port)
                end1.partWithPort = p1
                end2.partWithPort = p2
                provided.subject.ownedPort = p1
                required.subject.ownedPort = p2


    def disconnect(self, handle):
        super(ConnectorConnectBase, self).disconnect(handle)
        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to

        if isinstance(provided, items.ConnectorItem):
            provided = provided.head.connected_to
        if isinstance(required, items.ConnectorItem):
            required = required.tail.connected_to

        if provided and required:
            line.subject.unlink()
            provided.subject.ownedPort.unlink()
            required.subject.ownedPort.unlink()



class ComponentConnectorConnect(ConnectorConnectBase):
    """
    Connect two components which provide and require same interfaces.
    """
    component.adapts(items.ComponentItem, items.ConnectorItem)

    def glue(self, handle, port):
        glue_ok = super(ComponentConnectorConnect, self).glue(handle, port)
        line = self.line
        opposite = line.opposite(handle)

        return glue_ok


component.provideAdapter(ComponentConnectorConnect)



class AssemblyConnectorConnect(ConnectorConnectBase):
    """
    Connect assembly connectors with connector.
    """
    component.adapts(items.AssemblyConnectorItem, items.ConnectorItem)

    def glue(self, handle, port):
        """
        Allow to connect
        - connector's head to required port
        - connector's tail to provided port 
        """
        line = self.line
        opposite = line.opposite(handle)

        if isinstance(opposite.connected_to, items.AssemblyConnectorItem):
            glue_ok = False # no connection from assembly connector to assembly connector
        elif handle is line.head:
            glue_ok = port is self.element._required_port
        elif handle is line.tail:
            glue_ok = port is self.element._provided_port
        else:
            glue_ok = False

        return glue_ok and super(AssemblyConnectorConnect, self).glue(handle, port)


component.provideAdapter(AssemblyConnectorConnect)
