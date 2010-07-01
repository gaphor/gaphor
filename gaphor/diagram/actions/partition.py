"""
Activity Partition item.

TODO: partition can be resized only horizontally or vertically, therefore
- define constraints for horizontal and vertical handles
- reallocate handles in such way, so they clearly indicate horizontal
  or vertical size change
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem

class PartitionItem(NamedItem):
    __uml__ = UML.ActivityPartition

    __stereotype__ = {
        'external': lambda self: self.subject and self.subject.isExternal,
    }

    __style__   = {
        'min-size': (100, 300),
        'line-width': 2.4,
    }

    DELTA = 30

    def __init__(self, id=None):
        super(PartitionItem, self).__init__(id)
        self._toplevel = False
        self._bottom = False
        self._subpart = False
        self._hdmax = 0 # maximum subpartition header height


    def pre_update(self, context):
        super(PartitionItem, self).pre_update(context)

        # get subpartitions
        children = list(k for k in self.canvas.get_children(self)
                if isinstance(k, PartitionItem))

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
            wsum = sum(sl.width for sl in children)
            self._hdmax = max(sl._header_size[1] for sl in children)

            # extend width of swimline due the children but keep the height
            # untouched
            self.width = wsum

            dp = 0
            for sl in self.canvas.get_children(self):
                x, y = sl.matrix[4], sl.matrix[5]

                x = dp - x
                y =  - y + self._header_size[1] + self._hdmax - sl._header_size[1]
                sl.matrix.translate(x, y)

                sl.height = sl.min_height = max(0, self.height - self._header_size[1])
                dp += sl.width


    def draw(self, context):
        """
        By default horizontal partition is drawn. It is open on right side
        (or bottom side when horizontal).
        """
        cr = context.cairo
        cr.set_line_width(self.style.line_width)

        if self.subject and not self.subject.isDimension and self._toplevel:
            cr.move_to(0, 0)
            cr.line_to(self.width, 0)


        h = self._header_size[1]

        # draw outside lines if this item is toplevel partition
        if self._toplevel:
            cr.move_to(0, self.height)
            cr.line_to(0, h)
            cr.line_to(self.width, h)
            cr.line_to(self.width, self.height)

        super(PartitionItem, self).draw(context)

        if self._subpart:
            # header line for all subparitions
            hd = h + self._hdmax
            cr.move_to(0, hd)
            cr.line_to(self.width, hd)

        if self._subpart:
            # draw inside lines for all children but last one
            dp = 0
            for sl in self.canvas.get_children(self)[:-1]:
                dp += sl.width
                cr.move_to(dp, h)
                cr.line_to(dp, self.height)


        cr.stroke()

        if context.hovered or context.dropzone:
            cr.save()
            cr.set_dash((1.0, 5.0), 0)
            cr.set_line_width(1.0)
            cr.rectangle(0, 0, self.width, self.height)
            self.highlight(context)
            cr.stroke()
            cr.restore()


# vim:sw=4:et
