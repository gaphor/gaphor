"""
Activity Partition item.

TODO: partition can be resized only horizontally or vertically, therefore
- define constraints for horizontal and vertical handles
- reallocate handles in such way, so they clearly indicate horizontal
  or vertical size change
"""

from typing import List

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import (
    Box,
    SizeContext,
    Text,
    cairo_state,
    draw_highlight,
    stroke,
)
from gaphor.diagram.support import represents
from gaphor.diagram.text import VerticalAlign
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.ActivityPartition)
class PartitionItem(ElementPresentation, Named):

    DELTA = 30

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
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
        self.min_width = 100
        self.min_height = 300

    @property
    def toplevel(self):
        return self._toplevel

    def pre_update(self, context):
        assert self.canvas

        self._header_size = self.shape.size(
            SizeContext.from_context(context, self.style)
        )

        # get subpartitions
        children: List[PartitionItem] = list(
            k for k in self.canvas.get_children(self) if isinstance(k, PartitionItem)
        )

        self._toplevel = self.canvas.get_parent(self) is None
        self._subpart = len(children) > 0
        self._bottom = not self._toplevel and not self._subpart

        if self._toplevel:
            self._header_size = self._header_size[0], self.DELTA

        handles = self.handles()

        # toplevel partition controls the height
        # partitions at the very bottom control the width
        # middle partitions control nothing
        for h in handles:
            h.movable = False
            h.visible = False
        if self._bottom:
            h = handles[1]
            h.visible = h.movable = True
        if self._toplevel:
            h1, h2 = handles[2:4]
            h1.visible = h1.movable = True
            h2.visible = h2.movable = True

        if self._subpart:
            wsum: int = sum(sl.width for sl in children)
            self._hdmax = max(sl._header_size[1] for sl in children)

            # extend width of swimline due the children but keep the height
            # untouched
            self.width = wsum

            dp = 0
            for sl in self.canvas.get_children(self):
                x, y = sl.matrix[4], sl.matrix[5]

                x = dp - x
                y = -y + self._header_size[1] + self._hdmax - sl._header_size[1]
                sl.matrix.translate(x, y)

                sl.height = sl.min_height = max(0, self.height - self._header_size[1])
                dp += sl.width

    def draw_partition(self, box, context, bounding_box):
        """
        By default vertical partition is drawn. It is open on the bottom.
        """
        assert self.canvas

        cr = context.cairo
        cr.set_line_width(context.style["line-width"])

        if self.subject and not self.subject.isDimension and self._toplevel:
            cr.move_to(0, 0)
            cr.line_to(bounding_box.width, 0)

        h = self._header_size[1]

        # draw outside lines if this item is toplevel partition
        if self._toplevel:
            cr.move_to(0, bounding_box.height)
            cr.line_to(0, h)
            cr.line_to(bounding_box.width, h)
            cr.line_to(bounding_box.width, bounding_box.height)

        if self._subpart:
            # header line for all subparitions
            hd = h + self._hdmax
            cr.move_to(0, hd)
            cr.line_to(bounding_box.width, hd)

        if self._subpart:
            # draw inside lines for all children but last one
            dp = 0
            for sl in self.canvas.get_children(self)[:-1]:
                dp += sl.width
                cr.move_to(dp, h)
                cr.line_to(dp, bounding_box.height)

        stroke(context)

        if context.hovered or context.dropzone:
            with cairo_state(cr):
                cr.set_dash((1.0, 5.0), 0)
                cr.set_line_width(1.0)
                cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
                draw_highlight(context)
                cr.stroke()
