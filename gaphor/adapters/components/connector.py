"""
Assembly connector connections.
"""

from zope import interface, component

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.adapters.connectors import AbstractConnect

class AssemblyConnectorConnect(AbstractConnect):
    """
    Connect two components.
    """
    component.adapts(items.ComponentItem, items.ConnectorItem)

    element_factory = inject('element_factory')

    def glue(self, handle):
        glue_ok = super(AssemblyConnectorConnect, self).glue(handle)
        line = self.line
        opposite = line.opposite(handle)

        # get component items on required and provided side of a connector
        provided = opposite.connected_to
        required = self.element
        if line.head is opposite:
            provided, required = required, provided

        if required is not None and provided is not None:
            glue_ok = len(required.subject.required) > 0 \
                and len(provided.subject.provided) > 0
        return glue_ok


    def connect(self, handle):
        if super(AssemblyConnectorConnect, self).connect(handle):
            line = self.line
            provided = line.head.connected_to
            required = line.tail.connected_to
            opposite = line.opposite(handle)
            line.subject = self.element_factory.create(UML.Connector)


component.provideAdapter(AssemblyConnectorConnect)
