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
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.adapters.connectors import AbstractConnect


class ConnectorConnectBase(AbstractConnect):
    element_factory = inject('element_factory')
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
        connected = super(ConnectorConnectBase, self).connect(handle, port)
        if not connected:
            return False

        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to
        if isinstance(provided, items.ConnectorItem):
            provided = provided.head.connected_to
        if isinstance(required, items.ConnectorItem):
            required = required.tail.connected_to

        assert provided is None or isinstance(provided, items.ComponentItem)
        assert required is None or isinstance(required, items.ComponentItem)

        if provided and required:
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
            return True
        return False


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



class ComponentAssemblyConnectorConnect(ConnectorConnectBase):
    """
    Connect two components which provide and require same interfaces.
    """
    component.adapts(items.ComponentItem, items.ConnectorItem)

    def glue(self, handle, port):
        glue_ok = super(ComponentAssemblyConnectorConnect, self).glue(handle, port)
        line = self.line
        opposite = line.opposite(handle)

        # get component items on required and provided side of a connector
        if handle is line.head:
            provided = self.element
            required = opposite.connected_to
        else:
            provided = opposite.connected_to
            required = self.element

        if provided is not None and required is not None:
            glue_ok = len(self._get_interfaces(provided, required)) > 0
        return glue_ok


component.provideAdapter(ComponentAssemblyConnectorConnect)



class GroupAssemblyConnectorConnect(ConnectorConnectBase):
    """
    Group assembly connectors by connecting component and assembly
    connector.
    """
    component.adapts(items.ConnectorItem, items.ConnectorItem)

    def glue(self, handle, port):
        """
        Allow to connect
        - connector's tail to provided port 
        - connector's head to required port
        """
        glue_ok = super(GroupAssemblyConnectorConnect, self).glue(handle, port)
        line = self.line
        opposite = line.opposite(handle)

        if isinstance(opposite.connected_to, items.ConnectorItem):
            glue_ok = False
        elif handle is line.head:
            glue_ok = port is self.element._required_port
        elif handle is line.tail:
            glue_ok = port is self.element._provided_port

        return glue_ok


component.provideAdapter(GroupAssemblyConnectorConnect)
