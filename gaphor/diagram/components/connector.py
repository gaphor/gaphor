"""
Implementation of connector from Composite Structures and Components.

Only assembly connector (see chapter Components in UML specification) is
supported at the moment. The implementation is based on `ConnectorItem`
class and `InterfaceItem` class in assembly connector mode.

Assembly Connector
==================
To connect two components with assembly connector connect folded interface
and component items using connector item.

If component provides or requires connected interface, then assembly
connection in UML data model will be created and connector item will
display name of the interface. Otherwise, UML data model is not updated
and connector item does not display interface name.

Interface item in assembly connector mode does not display interface name
as it is displayed by connectors.

Connector item visualizes two UML metaclasses

- ConnectorEnd metaclass when connecting to interface item in assembly mode
- Connector metaclass in other cases

Using property pages of connector item, user can change superinterface of
connected interface.

Assembly Connector Mode of Interface Item
-----------------------------------------
Assembly connector notation is supported using interface item because of
its simplicity

- no need for additional assembly connector item
- because connection is made to specific interface, there is no need for
  performing a search for common interface of all connected components
- separate assembly connector item would require some rotation support,
  instead interface item's rotation capabilities are reused

Implementation Alternatives
---------------------------
There were several alternatives of assembly connector notation explored.

In Gaphor 0.8.x there was assembly connector item, with additional handles
and lines. User was dragging a handle of an additional line to connect to
a component, disadvantages

- item's connection behaviour is not consistent with other items
- rotation needs to be implemented

For Gaphor 0.14 and later, two other ideas were considered.

First one required assembly connector item as well. Connector item could
visualize ConnectorEnd and Connector UML metaclasses and it would be
used to connect assembly connector item and items of components. It is very
consistent with the rest of Gaphor application but

- it proved to be very complicated in implementation
- requires additional item

Second alternative was to have connector item only. It is very simple
concept in first place. When connector item connects two components, then
draw assembly connector icon in the middle of a line. The solution is very
simple in implementation and consistent with the rest of the application
until multiple components have to be connected with one assembly connector.

UML Specification Issues
========================
UML specification is not clear about interfaces as connectable elements
and connector's `kind` attribute.

Current implementation is subject to change in the future, when UML
specification clarifies issues described below.

See also http://www.omg.org/issues/uml2-rtf.open.html#Issue7251

Connector Kind
--------------
Chapter Components of UML specification adds `kind` attribute to connector
metaclass. This is enumeration with two possible values `assembly' and
`delegation'.

It is not clear what value should be assigned to `kind` attribute of
connector, which is defined between connectable elements like ports (not
characterized by interfaces), properties and parameters.

Interfaces as Connectable Elements
----------------------------------
Chapter Composite Structures in UML Superstructure 2.1.2 document does not
specify interfaces as connectable elements.

But definition of assembly connector says:

    An assembly connector is a connector between two components that
    defines that one component provides the services that another component
    requires. An assembly connector is a connector that is defined from
    a required _interface_ or port to a provided _interface_ or port.

Therefore, code of connector items is written with assumption, that
interfaces are connectable elements.
"""

import logging
from gaphor import UML
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM

from operator import attrgetter

logger = logging.getLogger(__name__)


class ConnectorItem(NamedLine):
    """
    Connector item line.

    Represents Connector UML metaclass. If connected to interface item in
    assembly connector mode, then `Connector.end` attribute represents
    appropriate `ConnectorEnd` UML metaclass instance.

    :Attributes:
     subject
        Connector UML metaclass instance.
     end
        ConnectorEnd UML metaclass instance.
     _interface
        Interface name, when connector is assembly connector.
    """

    __uml__ = UML.Connector
    __style__ = {"name-align": (ALIGN_CENTER, ALIGN_BOTTOM), "name-outside": True}

    def __init__(self, id=None, model=None):
        super(ConnectorItem, self).__init__(id, model)
        self._interface = self.add_text(
            "end.role.name", style={"text-align-group": "stereotype"}
        )
        self.watch("subject<Connector>.end.role.name", self.on_interface_name)

    def postload(self):
        super(ConnectorItem, self).postload()
        self.on_interface_name(None)

    def on_interface_name(self, event):
        """
        Callback used, when interface name changes (interface is referenced
        by `ConnectorItem.subject.end.role`).
        """
        try:
            self._interface.text = self.subject.end["it.role", 0].role.name
        except (IndexError, AttributeError) as e:
            logger.error(e)
            self._interface.text = ""
        else:
            self.request_update(matrix=False)

    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        if self.subject and self.subject.kind == "delegation":
            cr.move_to(15, -6)
            cr.line_to(0, 0)
            cr.line_to(15, 6)

    def save(self, save_func):
        super(ConnectorItem, self).save(save_func)
        # save_func('end', self.end)

    def load(self, name, value):
        if name == "end":
            pass  # self.end = value
        else:
            super(ConnectorItem, self).load(name, value)

    # def on_named_element_name(self, event):
    #    if isinstance(self.subject, UML.Connector):
    #        super(ConnectorItem, self).on_named_element_name(event)


# vim:sw=4:et:ai
