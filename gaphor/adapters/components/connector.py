"""
Assembly connector connections.
"""

import operator

from zope import interface, component

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.adapters.connectors import AbstractConnect

class AssemblyConnectorConnect(AbstractConnect):
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
        interfaces = []
        if c1 is not None and c2 is not None:
            provided = set(c1.subject.provided)
            required = set(c2.subject.required)
            interfaces = list(provided.intersection(required))
            interfaces.sort(key=operator.attrgetter('name'))
        return interfaces


    def glue(self, handle):
        glue_ok = super(AssemblyConnectorConnect, self).glue(handle)
        line = self.line
        opposite = line.opposite(handle)

        # get component items on required and provided side of a connector
        provided = opposite.connected_to
        required = self.element
        # head points to provided side of assembly connector
        if line.head is opposite:
            provided, required = required, provided

        glue_ok = len(self._get_interfaces(provided, required)) > 0
        return glue_ok


    def connect(self, handle):
        connected = super(AssemblyConnectorConnect, self).connect(handle)
        if not connected:
            return False

        line = self.line
        provided = line.head.connected_to
        required = line.tail.connected_to
        opposite = line.opposite(handle)
        line.subject = self.element_factory.create(UML.Connector)


component.provideAdapter(AssemblyConnectorConnect)
