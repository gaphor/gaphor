"""
Activity partition item.
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_MIDDLE


class PartitionItem(NamedItem):
    __uml__ = UML.ActivityPartition

#    __stereotype__ = {
#        'external': lambda self: self.isExternal,
#    }

    __style__   = {
#        'name-align': (ALIGN_LEFT, ALIGN_MIDDLE),
#        'name-rotated': True,
        'min-size': (100, 400),
    }
    def __init__(self, id=None):
        super(PartitionItem, self).__init__(id)


    def pre_update(self, context):
        super(PartitionItem, self).pre_update(context)

        # get subpartitions
        children = list(k for k in self.canvas.get_children(self)
                if isinstance(k, PartitionItem))

        has_parent = self.canvas.get_parent(self) is not None
        has_children = len(children) > 0

        handles = self.handles()
        for h in handles:
            h.movable = not (has_children or has_parent)
        if has_parent and not has_children:
            h = handles[2]
            h.movable = True


        if has_children:
            wsum = sum(sl.width for sl in children)
            hmax = max(sl.height for sl in children)
            hdmax = max(sl._header_size[1] for sl in children)

            self.width = wsum
            self.height = hmax + self._header_size[1] + 10

            dp = 0
            for sl in self.canvas.get_children(self):
                x, y = self.canvas.get_matrix_i2c(self).transform_point(dp, 0)
                x1, y1 = self.canvas.get_matrix_i2c(sl).transform_point(0, 0)

                # line up headers
                x = x - x1
                y = y - y1 + self._header_size[1] + hdmax - sl._header_size[1]
                sl.matrix.translate(x, y)

                sl.height = hmax

                sl.request_update()

                dp += sl.width


    def draw(self, context):
        """
        By default horizontal partition is drawn. It is open on right side
        (or bottom side when horizontal).
        """
        super(PartitionItem, self).draw(context)
        cr = context.cairo
        cr.set_line_width(2.5)

        has_parent = self.canvas.get_parent(self) is None

        if self.subject and not self.subject.isDimension and has_parent:
            cr.move_to(0, 0)
            cr.line_to(self.width, 0)

        h = self._header_size[1]
        cr.move_to(0, h)
        cr.line_to(self.width, h)

        if has_parent:
            cr.move_to(0, 0)
            cr.line_to(0, self.height)

        # but if is not last
        cr.move_to(self.width, 0)
        cr.line_to(self.width, self.height)

        cr.stroke()


# vim:sw=4:et
