"""
Implementation of connector from Composite Structures and Components.

Actually only assembly connector (see chapter Components in UML
specification) is implemented. This is done with ConnectorItem class.

Assembly Connector
==================
To connect two components with assembly connector

- first component has to provide at least one interface
- second one has to require the same interface or its superinterface

Using property pages, user can change

- the interface - interface is changed on all ends of assembly
  connector
- superinterface - the interface is changed on given end of assembly
  connector

UML Specificatiom Issues
========================
UML specification is not clear about interfaces as connectable elements
and connector's `kind` attribute.

Current implementation is subject to change in the future, when UML
specification clarifies issues described below.

See also http://www.omg.org/issues/uml2-rtf.open.html#Issue7251

Connector Kind
----------------------------------
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

Therefore, code of connectors is written with assumption, that interfaces
are connectable elements.
"""

from math import pi

from gaphor import UML
from gaphas.connector import Handle, PointPort
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM

class ConnectorItem(NamedLine):
    """
    Connector item.

    Connector is implemented as a line

    - by default, arrow is drawn at line's tail
    - assembly connector icon is drawn in the middle if connector is
      assembly connector
    - item is annotated with `delegate` stereotype if connector is
      delegate connector
    
    Assembly connector connects two components, its line ends describe
    provided and required sides of assembly connector

    - head shows provided interfaces
    - tail shows required interfaces
    """
    __uml__        = UML.Connector
    __style__   = {
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'name-outside': True,
    }

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, id=None):
        super(ConnectorItem, self).__init__(id)
        h1 = Handle(strength=0)
        h2 = Handle(strength=0)
        self._handles.insert(1, h1)
        self._handles.insert(2, h2)
        h1.movable = False
        h2.movable = False

        self.constraint(h1, line=(self.head, self.tail), align=0.5, delta=-15)
        self.constraint(h2, line=(self.head, self.tail), align=0.5, delta=15)

        self._provided_port = PointPort(h1.pos)
        self._required_port = PointPort(h2.pos)
        self._ports.append(self._provided_port)
        self._ports.append(self._required_port)


    is_assembly = property(lambda self: \
            self.subject is not None and self.subject.kind == 'assembly')


#    def draw_tail(self, context):
#        cr = context.cairo
#        cr.line_to(0, 0)
#        cr.stroke()
#
#        if not self.is_assembly:
#            cr.move_to(15, -6)
#            cr.line_to(0, 0)
#            cr.line_to(15, 6)


    def draw(self, context):
        super(ConnectorItem, self).draw(context)
        if isinstance(self.head.connected_to, ConnectorItem) \
                or isinstance(self.tail.connected_to, ConnectorItem):
            return
        cr = context.cairo
        cr.save()
        pos, angle = self._get_center_pos()
        cx, cy = pos
        cr.translate(cx, cy)
        cr.rotate(angle)
        cr.arc_negative(0, 0, self.RADIUS_REQUIRED, pi / 2 - 0.2, pi * 1.5 + 0.2)
        cr.move_to(0, 0)
        cr.arc(0, 0, self.RADIUS_PROVIDED, 0, pi*2)
        cr.stroke()
        cr.restore()


# vim:sw=4:et:ai
