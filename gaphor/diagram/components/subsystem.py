"""
Subsystem item represents a component with stereotype subsystem (see table
B.1 UML Keywords in UML 2.2 specification).

Subsystem item is part of components Gaphor package because it will show
components, nodes and other items within cotext of a subsystem. 

At the moment (in the future additionally) it makes only sense to use it on
use cases diagram.
"""

from gaphor import UML
from gaphor.diagram.component import ComponentItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP
from gaphor.diagram import uml

@uml(UML.Component, stereotype='subsystem')
class SubsystemItem(ComponentItem):
    __style__   = {
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }
    def __init__(self, id=None):
        super(SubsystemItem, self).__init__(id)


    def draw(self, context):
        super(SubsystemItem, self).draw(context)
        cr = context.cairo

        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()


# vim:sw=4:et
