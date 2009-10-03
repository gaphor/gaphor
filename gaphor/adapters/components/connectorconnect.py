"""
Connector connections.

Implemented using interface item in assembly connector mode, see
`gaphor.diagram.connector` module for details.
"""

from zope import component

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


    def get_connecting(self, iface, both=False):
        """
        Get items connecting to interface.

        :Parameters:
         iface
            Interface in question.
         both
            If true, then filter out one-side connections.
        """
        canvas = iface.canvas
        connected = canvas.get_connected_items(iface)
        if both:
            connected = [(l, h) for l, h in connected
                    if canvas.get_connected_to(l, l.opposite(h))]
        return connected


    def get_component(self, connector):
        """
        Get component connected by connector.
        """
        canvas = connector.canvas
        item = canvas.get_connected_to(connector, connector.head)[0]
        if not isinstance(item, items.ComponentItem):
            item = connector.get_connected_to(connector, connector.tail)[0]
        if not isinstance(item, items.ComponentItem):
            item = None
        return item


    def create_uml(self, connector, component, assembly, iface):
        """
        Create assembly connector UML metamodel for given connector item
        and component.

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

        connector.end = end
        component.subject.ownedPort = end.partWithPort


    def drop_uml(self, connector, component):
        """
        Destroy assembly connector UML metamodel existing between connector
        item and component item.

        :Parameters:
         connector
            Connector item.
         component
            Component item.
        """
        component.subject.ownedPort.unlink()
        connector.end.unlink()
        connector.end = None
        connector.subject = None


    def glue(self, handle, port):
        glue_ok = super(ConnectorConnectBase, self).glue(handle, port)

        iface = self.element
        component = self.get_connected_to_item(self.line.opposite(handle))

        if isinstance(component, items.InterfaceItem):
            component, iface = iface, component
            port = self.get_connected_to_port(self.line.opposite(handle))

        # connect only components and interfaces but not two interfaces nor
        # two components
        glue_ok = not (isinstance(component, items.ComponentItem) \
                and isinstance(iface, items.ComponentItem) \
                or isinstance(component, items.InterfaceItem) \
                and isinstance(iface, items.InterfaceItem))

        # if port type is known, then allow connection to proper port only
        if glue_ok and component is not None and iface is not None \
                and (port.required or port.provided):

            assert isinstance(component, items.ComponentItem)
            assert isinstance(iface, items.InterfaceItem)

            glue_ok = port.provided and iface.subject in component.subject.provided \
                or port.required and iface.subject in component.subject.required
            return glue_ok

        return glue_ok


    def connect(self, handle, port):
        super(ConnectorConnectBase, self).connect(handle, port)

        line = self.line
        canvas = self.line.canvas

        c1 = self.get_connected_to_item(line.head)
        c2 = self.get_connected_to_item(line.tail)
        if c1 and c2:
            # reference interface and component correctly
            iface = c1
            component = c2
            if isinstance(component, items.InterfaceItem):
                assert isinstance(iface, items.ComponentItem)
                component, iface = iface, component

            connected = self.get_connecting(iface, both=True)
            ports = set(self.get_connected_to(h) for _, h in connected)

            # to make an assembly at least two connector ends need to exist
            # also, two different ports of interface need to be connected
            if len(connected) > 1 and len(ports) == 2:
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

        iface = self.get_connected_to_item(line.head)
        if not isinstance(iface, items.InterfaceItem):
            iface = self.get_connected_to_item(line.tail)

        connected = self.get_connecting(iface, both=True)
        # find ports, which will stay connected after disconnection
        ports = set(self.get_connected_to_port(h) for c, h in connected if c is not self.line)

        # destroy whole assembly if one connected item stays
        # or only one port will stay connected
        if len(connected) == 2 or len(ports) == 1:
            connector = line.subject
            for conn, h in connected:
                c = self.get_component(conn)
                self.drop_uml(conn, c)
                conn.request_update(matrix=False)
            connector.unlink()
        else:
            c = self.get_component(line)
            self.drop_uml(line, c)



class ComponentConnectorConnect(ConnectorConnectBase):
    """
    Connection of connector item to a component.
    """
    component.adapts(items.ComponentItem, items.ConnectorItem)


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
        glue_ok = super(InterfaceConnectorConnect, self).glue(handle, port)
        iface = self.element
        glue_ok = glue_ok and iface.folded != iface.FOLDED_NONE
        if glue_ok:
            # find connected items, which are not connectors
            canvas = self.element.canvas
            connected = self.get_connecting(self.element)
            lines = [l for l, h in connected if not isinstance(l, items.ConnectorItem)]
            glue_ok = len(lines) == 0

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
        if not port.provided and not port.required:
            component = self.get_connected_to_item(self.line.opposite(handle))
            if component is not None and iface.subject in component.subject.required:
                pport, rport = rport, pport

            pport.provided = True
            rport.required = True

            iface._angle = rport.angle

            ports[(index + 1) % 4].connectable = False
            ports[(index + 3) % 4].connectable = False


    def disconnect(self, handle):
        super(InterfaceConnectorConnect, self).disconnect(handle)
        iface = self.element
        # about to disconnect last connector
        if len(list(self.get_connecting(iface))) == 1:
            ports = iface.ports()
            iface.folded = iface.FOLDED_PROVIDED
            iface._angle = ports[0].angle
            for p in ports:
                p.connectable = True
                p.provided = False
                p.required = False


component.provideAdapter(InterfaceConnectorConnect)
