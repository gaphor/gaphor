"""
Interface item implementation. There are several notations supported

- class box with interface stereotype
- folded interface
    - ball is drawn to indicate provided interface
    - socket is drawn to indicate required interface

Interface item can act as icon of assembly connector, see
`gaphor.diagram.connector` module documentation for details. *Documentation
of this module does not take into accout assembly connector icon mode.*

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
information, on UML data model level, that an interface depenends on itself
but it is not the intention of this (*unsupported*) notation.

For more examples of non-supported by Gaphor notation, see
http://martinfowler.com/bliki/BallAndSocket.html.


Folding and Connecting
----------------------
Current approach to folding and connecting lines to an interface is as
follows

- allow folding/unfolding of an interface only when there is only one
  implementation or depenedency usage connected
- when interface is folded, allow only one implementation or depenedency
  usage to be connected

Folding and unfolding is performed by `InterfacePropertyPage` class.
"""

import ast
from enum import Enum
from math import pi

from gaphas.canvas import Canvas
from gaphas.connector import LinePort
from gaphas.geometry import distance_line_point, distance_point_point
from gaphas.item import NE, NW, SE, SW

from gaphor import UML
from gaphor.diagram.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
)
from gaphor.diagram.classes.stereotype import stereotype_compartments
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, EditableText, IconBox, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight, VerticalAlign
from gaphor.UML.properties import attribute


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
    """
    Interface connection port.

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
        """
        Behaves like simple line port, but for folded interface suggests
        connection to the middle point of a port.
        """
        if self.is_folded():
            px = (self.start.x + self.end.x) / 2
            py = (self.start.y + self.end.y) / 2
            d = distance_point_point((px, py), pos)
            return (px, py), d
        else:
            d, pl = distance_line_point(self.start, self.end, pos)
            return pl, d


@represents(UML.Interface)
class InterfaceItem(ElementPresentation, Classified):
    """
    Interface item supporting class box, folded notations and assembly
    connector icon mode.

    When in folded mode, provided (ball) notation is used by default.
    """

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._folded = Folded.NONE
        self.side = Side.N

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
        ).watch("show_operations", self.update_shapes).watch(
            "subject[NamedElement].name"
        ).watch(
            "subject[NamedElement].namespace.name"
        ).watch(
            "subject.appliedStereotype", self.update_shapes
        ).watch(
            "subject.appliedStereotype.classifier.name"
        ).watch(
            "subject.appliedStereotype.slot", self.update_shapes
        ).watch(
            "subject.appliedStereotype.slot.definingFeature.name"
        ).watch(
            "subject.appliedStereotype.slot.value", self.update_shapes
        ).watch(
            "subject[Interface].supplierDependency", self.update_shapes
        )
        attribute_watches(self, "Interface")
        operation_watches(self, "Interface")

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=True)

    show_operations: attribute[int] = attribute("show_operations", int, default=True)

    def load(self, name, value):
        if name == "folded":
            self._folded = Folded(ast.literal_eval(value))
        else:
            super().load(name, value)

    def save(self, save_func):
        super().save(save_func)
        save_func("folded", self._folded.value)

    def _set_folded(self, folded):
        """
        Set folded notation.

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

            self.min_width, self.min_height = icon_size, icon_size
            self.width, self.height = icon_size, icon_size

            # update only h_se handle - rest of handles should be updated by
            # constraints
            h_nw = self._handles[NW]
            h_se = self._handles[SE]
            h_se.pos.x = h_nw.pos.x + self.min_width
            h_se.pos.y = h_nw.pos.y + self.min_height

            movable = False

        for h in self._handles:
            h.movable = movable

        self.update_shapes()

    folded = property(
        lambda s: s._folded,
        _set_folded,
        doc="Check or set folded notation, see Folded.* enum.",
    )

    def pre_update(self, context):
        assert isinstance(self.canvas, Canvas)
        connected_items = [c.item for c in self.canvas.get_connections(connected=self)]
        connectors = any(
            map(lambda i: isinstance(i.subject, UML.Connector), connected_items)
        )
        if connectors or self._folded != Folded.NONE:
            provided = connectors or any(
                map(
                    lambda i: isinstance(i.subject, UML.Implementation), connected_items
                )
            )
            required = any(
                map(lambda i: isinstance(i.subject, UML.Usage), connected_items)
            )
            if required and provided:
                self.folded = Folded.ASSEMBLY
            elif required:
                self.folded = Folded.REQUIRED
            else:
                self.folded = Folded.PROVIDED
            self.update_shapes(connectors=connectors)
        super().pre_update(context)

    def update_shapes(self, event=None, connectors=None):
        if self._folded == Folded.NONE:
            self.shape = self.class_shape()
        else:
            self.shape = self.ball_and_socket_shape(connectors)

    def class_shape(self):
        return Box(
            Box(
                Text(
                    text=lambda: UML.model.stereotypes_str(
                        self.subject, ("interface",)
                    ),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                Text(
                    text=lambda: from_package_str(self),
                    style={"font": "sans 8", "min-width": 0, "min-height": 0},
                ),
                style={"padding": (12, 4, 12, 4)},
            ),
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
            style={
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    def ball_and_socket_shape(self, connectors=None):
        assert self.canvas
        if connectors is None:
            # distinguish between None and []
            connected_items = [
                c.item for c in self.canvas.get_connections(connected=self)
            ]
            connectors = any(
                map(lambda i: isinstance(i.subject, UML.Connector), connected_items)
            )
        return IconBox(
            Box(
                style={"min-width": self.min_width, "min-height": self.min_height},
                draw=self.draw_interface_ball_and_socket,
            ),
            Text(
                text=lambda: UML.model.stereotypes_str(self.subject),
                style={"min-width": 0, "min-height": 0},
            ),
            EditableText(
                text=lambda: self.subject.name or "",
                style={
                    "font-weight": FontWeight.NORMAL if connectors else FontWeight.BOLD
                },
            ),
        )

    def draw_interface_ball_and_socket(self, _box, context, _bounding_box):
        cr = context.cairo

        h_nw = self._handles[NW]
        cx, cy = (h_nw.pos.x + self.width / 2, h_nw.pos.y + self.height / 2)

        if self._folded in (Folded.REQUIRED, Folded.ASSEMBLY):
            r = self.RADIUS_REQUIRED
            if self.side == Side.N:
                x, y = r * 2, r
            elif self.side == Side.E:
                x, y = r, r * 2
            elif self.side == Side.S:
                x, y = 0, r
            elif self.side == Side.W:
                x, y = r, 0

            cr.move_to(x, y)
            cr.arc_negative(
                cx, cy, self.RADIUS_REQUIRED, self.side.value, pi + self.side.value
            )

        if self._folded in (Folded.PROVIDED, Folded.ASSEMBLY):
            cr.move_to(cx + self.RADIUS_PROVIDED, cy)
            cr.arc(cx, cy, self.RADIUS_PROVIDED, 0, pi * 2)

        cr.stroke()
