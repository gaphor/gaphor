"""
Node item may represent a node or a device UML metamodel classes.

Grouping
========
Node item can group following items

- other nodes, which are represented with Node.nestedNode on UML metamodel
  level
- deployed artifacts using deployment
- components, which are parts of a node acting as structured classifier
  (nodes may have internal structures)

Node item grouping logic is implemented in `gaphor.adapters.grouping`
module.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.classifier import ClassifierItem

class NodeItem(ClassifierItem):
    """
    Representation of node or device from UML Deployment package.
    """

    __uml__ = uml2.Node, uml2.Device
    __stereotype__ = {
        'device': uml2.Device,
    }

    DEPTH = 10

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self.height = 50
        self.width = 120

    def draw_compartment(self, context):
        cr = context.cairo
        cr.save()
        super(NodeItem, self).draw_compartment(context)
        cr.restore()

        d = self.DEPTH
        w = self.width
        h = self.height

        cr.move_to(0, 0)
        cr.line_to(d, -d)
        cr.line_to(w + d, -d)
        cr.line_to(w + d, h - d)
        cr.line_to(w, h)
        cr.move_to(w, 0)
        cr.line_to(w + d, -d)

        cr.stroke()


# vim:sw=4:et
