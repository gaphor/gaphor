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

class ComponentAssemblyConnectorConnect(AbstractConnect):
    """
    Connect two components which provide and require same interfaces.
    """
    component.adapts(items.ComponentItem, items.ConnectorItem)

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


    def connect(self, handle, port):
        connected = super(ComponentAssemblyConnectorConnect, self).connect(handle, port)
        if not connected:
            return False

        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to

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
        super(ComponentAssemblyConnectorConnect, self).disconnect(handle)
        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to
        if provided and required:
            line.subject.unlink()
            provided.subject.ownedPort.unlink()
            required.subject.ownedPort.unlink()


component.provideAdapter(ComponentAssemblyConnectorConnect)



class GroupAssemblyConnectorConnect(AbstractConnect):
    """
    Group assembly connectors by connecting component and assembly
    connector.
    """
    component.adapts(items.ConnectorItem, items.ConnectorItem)

    element_factory = inject('element_factory')

    def glue(self, handle, port):
        glue_ok = super(GroupAssemblyConnectorConnect, self).glue(handle, port)
        line = self.line
        opposite = line.opposite(handle)

        if port is line._required_port or port is line._required_port:
            glue_ok = True
        return glue_ok


    def connect(self, handle, port):
        connected = super(GroupAssemblyConnectorConnect, self).connect(handle, port)
        if not connected:
            return False

        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to

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
        super(GroupAssemblyConnectorConnect, self).disconnect(handle)
        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to
        if provided and required:
            line.subject.unlink()
            provided.subject.ownedPort.unlink()
            required.subject.ownedPort.unlink()


component.provideAdapter(GroupAssemblyConnectorConnect)
