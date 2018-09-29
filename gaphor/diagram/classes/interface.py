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

from math import pi

from gaphas.connector import LinePort
from gaphas.geometry import distance_line_point, distance_point_point
from gaphas.item import NW, NE, SE, SW
from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.style import ALIGN_TOP, ALIGN_BOTTOM, ALIGN_CENTER


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

    :IVariables:
     angle
        Rotation angle.
     iface
        Interface owning port.

    """

    def __init__(self, start, end, iface, angle):
        super(InterfacePort, self).__init__(start, end)
        self.angle = angle
        self.iface = iface
        self.required = False
        self.provided = False


    def glue(self, pos):
        """
        Behaves like simple line port, but for folded interface suggests
        connection to the middle point of a port.
        """
        if self.iface.folded:
            px = (self.start.x + self.end.x) / 2
            py = (self.start.y + self.end.y) / 2
            d = distance_point_point((px, py), pos)
            return (px, py), d
        else:
            p1 = self.start
            p2 = self.end
            d, pl = distance_line_point(p1, p2, pos)
            return pl, d



class InterfaceItem(ClassItem):
    """
    Interface item supporting class box, folded notations and assembly
    connector icon mode.

    When in folded mode, provided (ball) notation is used by default.
    """

    __uml__        = UML.Interface
    __stereotype__ = {'interface': lambda self: self.drawing_style != self.DRAW_ICON}
    __style__ = {
        'icon-size': (20, 20),
        'icon-size-provided': (20, 20),
        'icon-size-required': (28, 28),
        'name-outside': False,
    }

    UNFOLDED_STYLE = {
        'text-align': (ALIGN_CENTER, ALIGN_TOP),
        'text-outside': False,
    }

    FOLDED_STYLE = {
        'text-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'text-outside': True,
    }

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    # Non-folded mode.
    FOLDED_NONE     = 0
    # Folded mode, provided (ball) notation.
    FOLDED_PROVIDED = 1
    # Folded mode, required (socket) notation.
    FOLDED_REQUIRED = 2
    # Folded mode, notation of assembly connector icon mode (ball&socket).
    FOLDED_ASSEMBLY = 3


    def __init__(self, id=None):
        ClassItem.__init__(self, id)
        self._folded = self.FOLDED_NONE
        self._angle = 0
        old_f = self._name.is_visible
        self._name.is_visible = lambda: old_f() and self._folded != self.FOLDED_ASSEMBLY

        handles = self._handles
        h_nw = handles[NW]
        h_ne = handles[NE]
        h_sw = handles[SW]
        h_se = handles[SE]

        # edge of element define default element ports
        self._ports = [
            InterfacePort(h_nw.pos, h_ne.pos, self, 0),
            InterfacePort(h_ne.pos, h_se.pos, self, pi / 2),
            InterfacePort(h_se.pos, h_sw.pos, self, pi),
            InterfacePort(h_sw.pos, h_nw.pos, self, pi * 1.5)
        ]

        self.watch('subject<Interface>.ownedAttribute', self.on_class_owned_attribute) \
            .watch('subject<Interface>.ownedOperation', self.on_class_owned_operation) \
            .watch('subject<Interface>.supplierDependency')


    @observed
    def set_drawing_style(self, style):
        """
        In addition to setting the drawing style, the handles are
        make non-movable if the icon (folded) style is used.
        """
        super(InterfaceItem, self).set_drawing_style(style)
        if self._drawing_style == self.DRAW_ICON:
            self.folded = self.FOLDED_PROVIDED # set default folded mode
        else:
            self.folded = self.FOLDED_NONE # unset default folded mode

    drawing_style = reversible_property(lambda self: self._drawing_style, set_drawing_style)

    def _is_folded(self):
        """
        Check if interface item is folded interface item.
        """
        return self._folded

    def _set_folded(self, folded):
        """
        Set folded notation.

        :param folded: Folded state, see FOLDED_* constants.
        """

        self._folded = folded

        if folded == self.FOLDED_NONE:
            movable = True
            draw_mode = self.DRAW_COMPARTMENT
            name_style = self.UNFOLDED_STYLE
        else:
            if self._folded == self.FOLDED_PROVIDED:
                icon_size = self.style.icon_size_provided
            else: # required interface or assembly icon mode
                icon_size = self.style.icon_size_required

            self.style.icon_size =  icon_size
            self.min_width, self.min_height = icon_size
            self.width, self.height = icon_size

            # update only h_se handle - rest of handles should be updated by
            # constraints
            h_nw = self._handles[NW]
            h_se = self._handles[SE]
            h_se.pos.x = h_nw.pos.x + self.min_width
            h_se.pos.y = h_nw.pos.y + self.min_height

            movable = False
            draw_mode = self.DRAW_ICON
            name_style = self.FOLDED_STYLE

        # call super method to avoid recursion (set_drawing_style calls
        # _set_folded method)
        super(InterfaceItem, self).set_drawing_style(draw_mode)
        self._name.style.update(name_style)

        for h in self._handles:
            h.movable = movable

        self.request_update()

    folded = property(_is_folded, _set_folded,
        doc="Check or set folded notation, see FOLDED_* constants.")


    def draw_icon(self, context):
        cr = context.cairo
        h_nw = self._handles[NW]
        cx, cy = h_nw.pos.x + self.width / 2, h_nw.pos.y + self.height / 2
        required = self._folded == self.FOLDED_REQUIRED or self._folded == self.FOLDED_ASSEMBLY
        provided = self._folded == self.FOLDED_PROVIDED or self._folded == self.FOLDED_ASSEMBLY
        if required:
            cr.save()
            cr.arc_negative(cx, cy, self.RADIUS_REQUIRED, self._angle, pi + self._angle)
            cr.restore()
        if provided:
            cr.move_to(cx + self.RADIUS_PROVIDED, cy)
            cr.arc(cx, cy, self.RADIUS_PROVIDED, 0, pi*2)
        cr.stroke()
        super(InterfaceItem, self).draw(context)


# vim:sw=4:et:ai
