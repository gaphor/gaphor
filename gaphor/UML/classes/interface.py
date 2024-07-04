"""Interface item implementation. There are several notations supported.

- class box with interface stereotype
- folded interface
    - ball is drawn to indicate provided interface
    - socket is drawn to indicate required interface

Interface item can act as icon of assembly connector, see
`gaphor.diagram.connector` module documentation for details. *Documentation
of this module does not take into account assembly connector icon mode.*

Folded Interface Item
=====================
Folded interface notation is reserved for very simple situations.
When interface is folded

- only an implementation can be connected (ball - provided interface)
- or only usage dependency can be connected (socket - required interface)

Above means that interface cannot be folded when

- both, usage dependency and implementation are connected
- any other lines are connected

Dependencies
------------
Dependencies between folded interfaces are *not supported*

+---------------------+---------------------+
|     *Supported*     |    *Unsupported*    |
+=====================+=====================+
| ::                  | ::                  |
|                     |                     |
|   |A|--(    O--|B|  |   |A|--(--->O--|B|  |
|        Z    Z       |        Z    Z       |
+---------------------+---------------------+

On above diagram, A requires interface Z and B provides interface Z.
Additionally, on the right diagram, Z is connected to itself with
dependency.

There is no need for additional dependency

- UML data model provides information, that Z is common for A and B
  (A requires Z, B provides Z)
- on a diagram, both folded interface items (required and provided)
  represent the same interface, which is easily identifiable with its name

Even more, adding a dependency between folded interfaces provides
information, on UML data model level, that an interface depends on itself
but, it is not the intention of this (*unsupported*) notation.

For more examples of non-supported by Gaphor notation, see
http://martinfowler.com/bliki/BallAndSocket.html.


Folding and Connecting
----------------------
Current approach to folding and connecting lines to an interface is as
follows

- allow folding/unfolding of an interface only when there is only one
  implementation or dependency usage connected
- when interface is folded, allow only one implementation or dependency
  usage to be connected

Folding and unfolding is performed by `InterfacePropertyPage` class.
"""

from enum import Enum
from math import pi

from gaphas.connector import LinePort
from gaphas.geometry import distance_line_point, distance_point_point
from gaphas.item import NE, NW, SE, SW

from gaphor import UML
from gaphor.core.modeling.presentation import literal_eval
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox, draw_border, stroke
from gaphor.diagram.support import represents
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
)
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment, text_stereotypes


class Folded(Enum):
    # Non-folded mode.
    NONE = 0
    # Folded mode, provided (ball) notation.
    PROVIDED = 1
    # Folded mode, required (socket) notation.
    REQUIRED = 2
    # Folded mode, notation of assembly connector icon mode (ball&socket).
    ASSEMBLY = 3


class Side(Enum):
    N = 0
    E = pi * 0.5
    S = pi
    W = pi * 1.5


class InterfacePort(LinePort):
    """Interface connection port.

    It is simple line port, which changes glue behaviour depending on
    interface folded state. If interface is folded, then
    `InterfacePort.glue` method suggests connection in the middle of the
    port.

    The port provides rotation angle information as well. Rotation angle
    is direction the port is facing (i.e. 0 is north, PI/2 is west, etc.).
    The rotation angle shall be used to determine rotation of required
    interface notation (socket's arc is in the same direction as the
    angle).
    """

    def __init__(self, start, end, is_folded, side):
        super().__init__(start, end)
        self.is_folded = is_folded
        # Used by connection logic:
        self.side = side

    def glue(self, pos):
        """Behaves like simple line port, but for folded interface suggests
        connection to the middle point of a port."""
        if self.is_folded():
            px = (self.start.x + self.end.x) / 2
            py = (self.start.y + self.end.y) / 2
            d = distance_point_point((px, py), pos)
            return (px, py), d
        else:
            d, pl = distance_line_point(self.start, self.end, pos)
            return pl, d


@represents(UML.Interface)
class InterfaceItem(Classified, ElementPresentation):
    """Interface item supporting class box, folded notations and assembly
    connector icon mode.

    When in folded mode, provided (ball) notation is used by default.
    """

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram, id, width=self.RADIUS_PROVIDED * 2, height=self.RADIUS_PROVIDED * 2
        )
        self._folded = Folded.NONE
        self._side = Side.N

        handles = self.handles()
        h_nw = handles[NW]
        h_ne = handles[NE]
        h_sw = handles[SW]
        h_se = handles[SE]

        def is_folded():
            return self._folded != Folded.NONE

        # edge of element define default element ports
        self._ports = [
            InterfacePort(h_nw.pos, h_ne.pos, is_folded, Side.N),
            InterfacePort(h_ne.pos, h_se.pos, is_folded, Side.E),
            InterfacePort(h_se.pos, h_sw.pos, is_folded, Side.S),
            InterfacePort(h_sw.pos, h_nw.pos, is_folded, Side.W),
        ]

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch("subject.name").watch(
            "subject.namespace.name"
        ).watch("subject[Interface].supplierDependency", self.update_shapes)
        attribute_watches(self, "Interface")
        operation_watches(self, "Interface")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=True)

    show_operations: attribute[int] = attribute("show_operations", int, default=True)

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, side):
        self._side = side

    def load(self, name, value):
        if name == "folded":
            self._folded = Folded(literal_eval(value))
        else:
            super().load(name, value)

    def save(self, save_func):
        super().save(save_func)
        save_func("folded", self._folded.value)

    @property
    def folded(self):
        """Check or set folded notation, see Folded.* enum."""
        return self._folded

    @folded.setter
    def folded(self, folded):
        """Set folded notation.

        :param folded: Folded state, see Folded.* enum.
        """
        if self._folded == folded:
            return

        self._folded = folded

        if folded == Folded.NONE:
            movable = True
        else:
            if self._folded == Folded.PROVIDED:
                icon_size = self.RADIUS_PROVIDED * 2
            else:  # required interface or assembly icon mode
                icon_size = self.RADIUS_REQUIRED * 2

            self.min_width = self.min_height = self.width = self.height = icon_size

            movable = False

        for h in self._handles:
            h.movable = movable

        self.update_shapes()

    def update_shapes(self, event=None):
        connected_items = [
            c.item for c in self.diagram.connections.get_connections(connected=self)
        ]
        connectors = any(isinstance(i.subject, UML.Connector) for i in connected_items)
        if connectors or self._folded != Folded.NONE:
            provided = connectors or any(
                isinstance(i.subject, UML.InterfaceRealization) for i in connected_items
            )
            required = any(isinstance(i.subject, UML.Usage) for i in connected_items)
            if required and provided:
                self.folded = Folded.ASSEMBLY
            elif required:
                self.folded = Folded.REQUIRED
            else:
                self.folded = Folded.PROVIDED

        if self._folded == Folded.NONE:
            self.shape = self.class_shape()
        else:
            self.shape = self.ball_and_socket_shape(connectors)

    def class_shape(self):
        return Box(
            name_compartment(self, lambda: [self.diagram.gettext("interface")]),
            *(
                self.show_attributes
                and self.subject
                and [attributes_compartment(self.subject)]
                or []
            ),
            *(
                self.show_operations
                and self.subject
                and [operations_compartment(self.subject)]
                or []
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_border,
        )

    def ball_and_socket_shape(self, connectors=None):
        if connectors is None:
            # distinguish between None and []
            connected_items = [
                c.item for c in self.diagram.connections.get_connections(connected=self)
            ]
            connectors = any(
                isinstance(i.subject, UML.Connector) for i in connected_items
            )
        return IconBox(
            Box(
                draw=self.draw_interface_ball_and_socket,
            ),
            text_stereotypes(self),
            text_name(self),
        )

    def draw_interface_ball_and_socket(self, _box, context, _bounding_box):
        cr = context.cairo

        h_nw = self._handles[NW]
        cx, cy = (h_nw.pos.x + self.width / 2, h_nw.pos.y + self.height / 2)

        if self._folded in (Folded.REQUIRED, Folded.ASSEMBLY):
            r = self.RADIUS_REQUIRED
            if self._side == Side.N:
                x, y = r * 2, r
            elif self._side == Side.E:
                x, y = r, r * 2
            elif self._side == Side.S:
                x, y = 0, r
            elif self._side == Side.W:
                x, y = r, 0

            cr.move_to(x, y)
            cr.arc_negative(
                cx, cy, self.RADIUS_REQUIRED, self._side.value, pi + self._side.value
            )

        if self._folded in (Folded.PROVIDED, Folded.ASSEMBLY):
            cr.move_to(cx + self.RADIUS_PROVIDED, cy)
            cr.arc(cx, cy, self.RADIUS_PROVIDED, 0, pi * 2)

        stroke(context, fill=True)
