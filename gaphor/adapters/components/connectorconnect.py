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

    def get_component(self, connector):
        """
        Get component connected by connector.
        """
        item = connector.head.connected_to
        if not isinstance(item, items.ComponentItem):
            item = connector.tail.connected_to
        if not isinstance(item, items.ComponentItem):
            item = None
        return item


    def create_uml(self, connector, component, assembly, iface):
        """
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

        end =  self.element_factory.create(UML.ConnectorEnd)
        end.role = iface
        end.partWithPort = self.element_factory.create(UML.Port)
        assembly.end = end

        component.subject.ownedPort = end.partWithPort


    def connect(self, handle, port):
        super(ConnectorConnectBase, self).connect(handle, port)

        line = self.line
        canvas = self.line.canvas

        if line.head.connected_to and line.tail.connected_to:
            iface = line.head.connected_to
            component = line.tail.connected_to

            # reference interface and component correctly
            if isinstance(component, items.InterfaceItem):
                assert isinstance(iface, items.ComponentItem)
                component, iface = iface, component

            connected = canvas.get_connected_items(iface)
            if len(connected) > 1:
                # find assembly connector
                assembly = None
                for conn, h in connected:
                    if conn.subject:
                        assembly = conn.subject
                        assert assembly.kind == 'assembly'
                        break

                if assembly is None:
                    assembly =  self.element_factory.create(UML.Connector)
                    assembly.kind = 'assembly'
                    for c, h in connected:
                        self.create_uml(c, self.get_component(c), assembly, iface.subject)
                else:
                    self.create_uml(line, component, assembly, iface.subject)


    def disconnect(self, handle):
        super(ConnectorConnectBase, self).disconnect(handle)
        line = self.line
        if line.subject is None:
            return

        iface = line.head.connected_to
        if not isinstance(iface, items.InterfaceItem):
            iface = line.tail.connected_to

        connected = iface.canvas.get_connected_items(iface)
        if len(connected) == 2:
            line.subject.unlink()
            for conn, h in connected:
                c = self.get_component(conn)
                c.subject.ownedPort.unlink()
        else:
            line.subject = None
            c = self.get_component(line)
            c.subject.ownedPort.unlink()



class ComponentConnectorConnect(ConnectorConnectBase):
    """
    Connection of connector item to a component.
    """
    component.adapts(items.ComponentItem, items.ConnectorItem)

    def glue(self, handle, port):
        glue_ok = super(ComponentConnectorConnect, self).glue(handle, port)

        opposite = self.line.opposite(handle)
        glue_ok = not isinstance(opposite.connected_to, items.ComponentItem)

        return glue_ok


component.provideAdapter(ComponentConnectorConnect)


class InterfaceConnectorConnect(ConnectorConnectBase):
    """
    Connect connector to an interface to maintain assembly connection.

    See also `AbstractConnect` class for exception of interface item
    connections.
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
