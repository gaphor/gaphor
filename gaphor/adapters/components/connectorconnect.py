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


def _interfaces(pcomp, rcomp):
    """
    Return list of sorted interfaces common to components connected by
    assembly connector.
    """
    provided = set()
    required = set()
    for c in pcomp:
        provided.update(c.subject.provided)

    for c in rcomp:
        required.update(c.subject.required)

    interfaces = list(provided.intersection(required))
    interfaces.sort(key=operator.attrgetter('name'))
    return interfaces


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


    def connect(self, handle, port):
        super(ConnectorConnectBase, self).connect(handle, port)

        line = self.line
        assembly = line.head.connected_to
        if not isinstance(assembly, items.AssemblyConnectorItem):
            assembly = line.tail.connected_to

        if isinstance(assembly, items.AssemblyConnectorItem):
            def get_component(line):
                item = line.head.connected_to
                if not isinstance(item, items.ComponentItem):
                    item = line.tail.connected_to
                if not isinstance(item, items.ComponentItem):
                    item = None
                return item

                    
            def fetch_components(port):
                components = []
                for c in port._connected:
                    item = get_component(c)
                    if item is not None:
                        components.append(item)
                return components

            pcomp = fetch_components(assembly._provided_port)
            rcomp = fetch_components(assembly._required_port)

            interfaces = _interfaces(pcomp, rcomp)

            if len(interfaces) > 0:
                # create uml data model
                connector =  self.element_factory.create(UML.Connector)
                connector.kind = 'assembly'
                assembly.subject = connector

                iface = interfaces[0]

                def create(component, conn):
                    end = self.element_factory.create(UML.ConnectorEnd)
                    end.role = iface
                    connector.end = end
                    end.partWithPort = self.element_factory.create(UML.Port)

                    conn.subject = end
                    component.subject.ownedPort = end.partWithPort

                for conn in assembly._provided_port._connected:
                    item = get_component(conn)
                    if item is not None:
                        create(item, conn)

                for conn in assembly._required_port._connected:
                    item = get_component(conn)
                    if item is not None:
                        create(item, conn)


    def disconnect(self, handle):
        super(ConnectorConnectBase, self).disconnect(handle)
        line = self.line
        if line.subject is None:
            return
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

        # no connection from assembly connector to assembly connector
        glue_ok = not isinstance(opposite.connected_to, items.AssemblyConnectorItem)

        return glue_ok and super(AssemblyConnectorConnect, self).glue(handle, port)


    def connect(self, handle, port):
        if isinstance(self.element, items.AssemblyConnectorItem):
            port._connected.append(self.line)
        super(AssemblyConnectorConnect, self).connect(handle, port)


    def disconnect(self, handle, port):
        super(AssemblyConnectorConnect, self).connect(handle, port)
        if isinstance(self.element, items.ComponentItem):
            port._connected.remove(self.element)


component.provideAdapter(AssemblyConnectorConnect)

class InterfaceConnectorConnect(AbstractConnect):
    """
    Connect connector to an interface to maintain assembly connection.

    Inspired by
    http://www.visual-paradigm.com/VPGallery/diagrams/Component.html
    """
    component.adapts(items.InterfaceItem, items.ConnectorItem)

    def glue(self, handle, port):
        """
        Allow glueing to folded interface only and when only connectors are
        connected.
        """
        glue_ok = False
        if self.element.folded:
            # find connected items, which are not connectors
            canvas = self.element.canvas
            connected = [d for d in canvas.get_connected_items(self.element)
                    if not isinstance(d[0], items.ConnectorItem)]
            glue_ok = len(connected) == 0

        return glue_ok


    def connect(self, handle, port):
        super(InterfaceConnectorConnect, self).connect(handle, port)

        iface = self.element
        iface.folded = iface.FOLDED_ASSEMBLY
         
        # determine required and provided ports
        pport = port
        ports = iface.ports()
        index = ports.index(port)
        rport = ports[(index + 2) % 4]
        if not pport.provided and not pport.required:
            pport.provided = True
            rport.required = True
            iface._angle = rport.angle

            ports[(index + 1) % 4].connectable = False
            ports[(index + 3) % 4].connectable = False


    def disconnect(self, handle):
        super(InterfaceConnectorConnect, self).disconnect(handle)
        iface = self.element
        # about to disconnect last connector
        if len(iface.canvas.get_connected_items(iface)) == 1:
            ports = iface.ports()
            iface.folded = iface.FOLDED_PROVIDED
            iface._angle = ports[0].angle
            for p in ports:
                p.connectable = True
                p.provided = False
                p.required = False


component.provideAdapter(InterfaceConnectorConnect)
