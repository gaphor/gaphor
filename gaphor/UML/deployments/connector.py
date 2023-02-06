"""Implementation of connector from Composite Structures and Components.

Only assembly connector (see chapter Components in UML specification) is
supported at the moment. The implementation is based on `ConnectorItem`
class and `InterfaceItem` class in assembly connector mode.

Assembly Connector
==================
To connect two components with assembly connector connect folded interface
and component items using connector item.

If component provides or requires a connected interface, then assembly
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
visualize ConnectorEnd and Connector UML metaclasses, and it would be
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

from gaphor import UML
from gaphor.core.format import format
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, cairo_state
from gaphor.diagram.support import represents
from gaphor.UML.classes.association import get_center_pos
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Connector)
class ConnectorItem(Named, LinePresentation[UML.Connector]):
    """Connector item line.

    Represents Connector UML metaclass. If connected to interface item in
    assembly connector mode, then `Connector.end` attribute represents
    appropriate `ConnectorEnd` UML metaclass instance.

    :Attributes:
     subject
        Connector UML metaclass instance.
     end
        ConnectorEnd UML metaclass instance.
    """

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                Text(
                    text=lambda: stereotypes_str(self.subject),
                ),
                Text(text=lambda: self.subject.name or ""),
                Text(
                    text=lambda: ", ".join(
                        self.subject.informationFlow[:].conveyed[:].name
                    )
                ),
                # Also support SysML ItemFlow:
                Text(
                    text=lambda: stereotypes_str(
                        self.subject.informationFlow[0].itemProperty.type,  # type: ignore[attr-defined]
                        raaml_stereotype_workaround(
                            self.subject.informationFlow[0].itemProperty.type  # type: ignore[attr-defined]
                        ),
                    )
                    if self.subject.informationFlow
                    else ""
                ),
                Text(
                    text=lambda: format(
                        self.subject.informationFlow[0].itemProperty, type=True  # type: ignore[attr-defined]
                    )
                    if self.subject.informationFlow
                    else ""
                ),
            ),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Connector].informationFlow.informationSource")
        self.watch("subject[Connector].informationFlow.conveyed.name")
        self.watch("subject[Connector].informationFlow[ItemFlow].itemProperty.name")
        self.watch(
            "subject[Connector].informationFlow[ItemFlow].itemProperty.type.name"
        )
        self.watch(
            "subject[Connector].informationFlow[ItemFlow].itemProperty.type.appliedStereotype.classifier.name"
        )

    def draw(self, context):
        super().draw(context)
        subject = self.subject
        if subject and subject.informationFlow:
            inv = (
                1
                if (subject.end[0].role in subject.informationFlow[:].informationTarget)
                else -1
            )
            handles = self.handles()
            pos, angle = get_center_pos(handles)
            with cairo_state(context.cairo) as cr:
                cr.translate(*pos)
                cr.rotate(angle)
                cr.move_to(0, 0)
                cr.line_to(12 * inv, 8)
                cr.line_to(12 * inv, -8)
                cr.fill()

    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        if self.subject and self.subject.kind == "delegation":
            cr.move_to(15, -6)
            cr.line_to(0, 0)
            cr.line_to(15, 6)


def raaml_stereotype_workaround(element):
    """This is a temporary fix to ensure ItemFlow is showing proper stereotypes
    for Controller, Feedback and ControlAction from RAAML."""
    if not element:
        return ()

    name: str = type(element).__name__
    if name in {"Controller", "Feedback", "ControlAction"}:
        return (name[0].lower() + name[1:],)
    return ()
