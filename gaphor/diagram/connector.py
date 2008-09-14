"""
Connectors and connector ends from Composite Structures and Components.

Actually only Assembly connector (see Components in UML specs) is
implemented. This is done with AssemblyConnectorItem class.
AssemblyConnectorItem uses ConnectorEndItem (see ProvidedConnectorEndItem
and RequiredConnectorEndItem classes) instances to connect to components.

Component should provide at least one interface so ProvidedConnectorEndItem
can be connected to it. If there are more than one provided interfaces,
then user can choose appropriate one from ProvidedConnectorEndItem object
menu. Above also applies for required stuff.

UML Specificatiom Issues
========================
In some areas UML specification is not clear about connector kind and
interfaces as connectable elements, see also

    http://modeldrivenengineering.org/bin/view/Umlrtf/CurrentProposals

Connector Kind
----------------------------------
Components chapter adds kind attribute to connector class. According to UML
specs it is enumeration with two possible values 'assembly' and
'delegation'.

This is an issue for connector between connectable elements like
properties, parameters or more specific ports not characterized by
interfaces. It is not clear what value should be assigned for connector
kind for connectors between such elements.


Interfaces as Connectable Elements
----------------------------------
Composite Structures chapter in UML Superstructure (formal 05/07/04)
document does not specify interfaces as connectable elements.

But definition of assembly connector says:

    An assembly connector is a connector between two components that
    defines that one component provides the services that another component
    requires. An assembly connector is a connector that is defined from a
    required _interface_ or port to a provided _interface_ or port

Therefore, code of connectors is written with assumption, that interfaces
are connectable elements.

This is subject to change in the future when UML specification clarifies in
this area.
"""

from math import pi

from gaphor import UML
from gaphas.item import NW
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM

class AssemblyConnectorItem(NamedItem):
    """
    Assembly connector item.

    It has exactly two free connector end items.

    Connector end items are added and removed from assembly connector using
    canvas groupable interface.

    Assembly connector item distinguishes between two kind of main points.
    One is for connector end items, which connect to provided interfaces/ports.
    Other is for required interfaces/ports.
    """
    __uml__        = UML.Connector
    __style__   = {
        'min-size':   (20, 20),
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'name-outside': True,
    }

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, id=None):
        super(AssemblyConnectorItem, self).__init__(id)
        for h in self.handles():
            h.movable = False

    def draw(self, context):
        super(AssemblyConnectorItem, self).draw(context)
        cr = context.cairo
        h_nw = self._handles[NW]
        cx, cy = h_nw.x + self.width / 2, h_nw.y + self.height / 2
        cr.move_to(cx, cy + self.RADIUS_REQUIRED)
        cr.arc_negative(cx, cy, self.RADIUS_REQUIRED, pi / 2 - 0.2, pi * 1.5 + 0.2)
        cr.move_to(cx + self.RADIUS_PROVIDED, cy)
        cr.arc(cx, cy, self.RADIUS_PROVIDED, 0, pi*2)
        cr.stroke()
