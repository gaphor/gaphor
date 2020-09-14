"""Activity Partition item.

TODO: partition can be resized only horizontally or vertically, therefore
- define constraints for horizontal and vertical handles
- reallocate handles in such way, so they clearly indicate horizontal
  or vertical size change
"""

from typing import List

from gaphas.item import NE, NW

from gaphor import UML
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, cairo_state, draw_highlight, stroke
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.ActivityPartition)
class PartitionItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.parent = None
        self._toplevel = False
        self._bottom = False
        self._subpart = False
        self._hdmax = 0  # maximum subpartition header height

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(
                    self.subject,
                    self.subject and self.subject.isExternal and ("external",) or (),
                ),
            ),
            Text(text=lambda: self.subject.name or ""),
            style={
                "min-width": 0,
                "min-height": 0,
                "line-width": 2.4,
                "vertical-align": VerticalAlign.TOP,
                "padding": (2, 2, 2, 2),
            },
            draw=self.draw_partition,
        )
        self.min_width = 150
        self.min_height = 300

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")

    @property
    def toplevel(self):
        return self._toplevel

    def pre_update(self, context):
        assert self.canvas

        # get subpartitions
        children: List[PartitionItem] = [
            k for k in self.canvas.get_children(self) if isinstance(k, PartitionItem)
        ]

        self._toplevel = self.canvas.get_parent(self) is None
        self._subpart = len(children) > 0
        self._bottom = not (self._toplevel or self._subpart)

        h1, h2 = self.handles()[2:4]
        h1.visible = h1.movable = True
        h2.visible = h2.movable = True

    def draw_partition(self, box, context, bounding_box):
        """Draw a vertical partition.

        The partitions are open on the bottom.
        """
        assert self.canvas

        cr = context.cairo
        cr.set_line_width(context.style["line-width"])

        if self.parent:
            parent_handles = self.parent.handles()
            parent_h_ne = parent_handles[NE]
            x, y = self.canvas.get_matrix_i2c(self.parent).transform_point(
                *parent_h_ne.pos
            )
            x, y = self.canvas.get_matrix_c2i(self).transform_point(x, y)

            handles = self.handles()
            h_nw = handles[NW]
            h_ne = handles[NE]

            h_nw.pos.x = x
            h_ne.pos.y = y

        # Header left, top, and right outline
        cr.move_to(0, bounding_box.height)
        cr.line_to(0, 0)
        cr.line_to(bounding_box.width, 0)
        cr.line_to(bounding_box.width, bounding_box.height)

        # Header bottom outline
        cr.move_to(0, bounding_box.height)
        h = self.shape.size(context)[1]
        cr.line_to(0, h)
        cr.line_to(bounding_box.width, h)
        cr.line_to(bounding_box.width, bounding_box.height)

        stroke(context)

        if context.hovered or context.dropzone:
            with cairo_state(cr):
                cr.set_dash((1.0, 5.0), 0)
                cr.set_line_width(1.0)
                cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
                draw_highlight(context)
                cr.stroke()
